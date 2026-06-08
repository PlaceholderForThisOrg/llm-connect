import argparse
import csv
import json
import os
import statistics
import time
from pathlib import Path
from typing import Any

import httpx


def _load_cases(path: Path) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                cases.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at line {line_no}: {exc}") from exc
    return cases


def _headers(token: str) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _create_conversation(client: httpx.Client, token: str) -> str:
    response = client.post("/api/v1/me/conversations/", headers=_headers(token))
    response.raise_for_status()
    body = response.json()
    conversation_id = body.get("id")
    if not conversation_id:
        raise ValueError("Conversation creation succeeded but response has no 'id'.")
    return str(conversation_id)


def _chat(
    client: httpx.Client,
    token: str,
    conversation_id: str,
    question: str,
) -> tuple[str, float]:
    t0 = time.perf_counter()
    response = client.post(
        f"/api/v1/me/conversations/{conversation_id}/messages/",
        json={"content": question},
        headers=_headers(token),
    )
    latency_ms = (time.perf_counter() - t0) * 1000
    response.raise_for_status()
    body = response.json()
    return str(body.get("content", "")), latency_ms


def _retrieve_context(
    client: httpx.Client,
    question: str,
    limit: int,
) -> list[dict[str, Any]]:
    response = client.get(
        "/api/v1/atomic-points/rag/search",
        params={"q": question, "limit": limit},
    )
    response.raise_for_status()
    body = response.json()
    return body if isinstance(body, list) else []


def _normalize_ids(values: Any) -> list[str]:
    if not values:
        return []
    return [str(value) for value in values]


def _compute_retrieval_metrics(
    hits: list[dict[str, Any]],
    expected_ids: list[str],
) -> dict[str, float | None]:
    if not expected_ids:
        return {
            "hit_at_k": None,
            "mrr": None,
        }

    ranked_ids = [str(hit.get("atomic_point_id")) for hit in hits]
    hit = 0.0
    reciprocal_rank = 0.0

    for idx, atomic_point_id in enumerate(ranked_ids, start=1):
        if atomic_point_id in expected_ids:
            hit = 1.0
            reciprocal_rank = 1.0 / idx
            break

    return {
        "hit_at_k": hit,
        "mrr": reciprocal_rank,
    }


def _try_run_ragas(
    rows: list[dict[str, Any]],
) -> tuple[dict[str, float], list[dict[str, Any]], str | None]:
    try:
        from datasets import Dataset
        from ragas import evaluate
        from ragas.metrics import (
            answer_relevancy,
            context_precision,
            context_recall,
            faithfulness,
        )
    except ImportError as exc:
        return {}, rows, f"Ragas dependencies are not installed: {exc}"

    if not os.environ.get("OPENAI_API_KEY"):
        return {}, rows, "OPENAI_API_KEY is not set, so Ragas grading was skipped."

    ragas_rows = []
    for row in rows:
        if row["status"] != "ok":
            continue
        ragas_rows.append(
            {
                "question": row["question"],
                "answer": row["answer"],
                "contexts": row["contexts"],
                "ground_truth": row["ground_truth"],
            }
        )

    if not ragas_rows:
        return {}, rows, "No successful rows available for Ragas evaluation."

    dataset = Dataset.from_list(ragas_rows)
    result = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_recall,
            context_precision,
        ],
    )

    summary: dict[str, float] = {}
    if hasattr(result, "to_pandas"):
        frame = result.to_pandas()
        for key in [
            "faithfulness",
            "answer_relevancy",
            "context_recall",
            "context_precision",
        ]:
            if key in frame.columns:
                numeric_values = [float(v) for v in frame[key].dropna().tolist()]
                if numeric_values:
                    summary[key] = round(statistics.mean(numeric_values), 4)

        successful_indexes = [
            index for index, row in enumerate(rows) if row["status"] == "ok"
        ]
        for frame_index, row_index in enumerate(successful_indexes):
            if frame_index >= len(frame):
                break
            for key in summary:
                value = frame.iloc[frame_index].get(key)
                if value is not None:
                    rows[row_index][key] = round(float(value), 4)
    elif hasattr(result, "to_dict"):
        raw = result.to_dict()
        for key in [
            "faithfulness",
            "answer_relevancy",
            "context_recall",
            "context_precision",
        ]:
            value = raw.get(key)
            if value is not None:
                summary[key] = round(float(value), 4)

    return summary, rows, None


def run_eval(
    *,
    base_url: str,
    auth_token: str,
    cases: list[dict[str, Any]],
    rag_limit: int,
    timeout_s: float,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    with httpx.Client(base_url=base_url.rstrip("/"), timeout=timeout_s) as client:
        for case in cases:
            question = case["question"]
            ground_truth = case.get("ground_truth", "")
            expected_ids = _normalize_ids(case.get("expected_atomic_point_ids"))
            try:
                conversation_id = _create_conversation(client, auth_token)
                answer, latency_ms = _chat(
                    client=client,
                    token=auth_token,
                    conversation_id=conversation_id,
                    question=question,
                )
                rag_hits = _retrieve_context(client, question, rag_limit)
                contexts = [
                    str(hit.get("semantic_text", "")) for hit in rag_hits if hit.get("semantic_text")
                ]
                retrieval_metrics = _compute_retrieval_metrics(rag_hits, expected_ids)
                results.append(
                    {
                        "id": case.get("id", ""),
                        "question": question,
                        "ground_truth": ground_truth,
                        "answer": answer,
                        "status": "ok",
                        "latency_ms": round(latency_ms, 2),
                        "conversation_id": conversation_id,
                        "retrieved_atomic_point_ids": [
                            str(hit.get("atomic_point_id")) for hit in rag_hits
                        ],
                        "contexts": contexts,
                        "context_count": len(contexts),
                        "hit_at_k": retrieval_metrics["hit_at_k"],
                        "mrr": retrieval_metrics["mrr"],
                    }
                )
            except Exception as exc:  # noqa: BLE001
                results.append(
                    {
                        "id": case.get("id", ""),
                        "question": question,
                        "ground_truth": ground_truth,
                        "answer": "",
                        "status": "error",
                        "latency_ms": 0.0,
                        "conversation_id": "",
                        "retrieved_atomic_point_ids": [],
                        "contexts": [],
                        "context_count": 0,
                        "hit_at_k": None,
                        "mrr": None,
                        "error": str(exc),
                    }
                )

    return results


def _write_outputs(prefix: Path, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    prefix.parent.mkdir(parents=True, exist_ok=True)
    json_path = prefix.with_suffix(".json")
    csv_path = prefix.with_suffix(".csv")
    summary_path = prefix.with_suffix(".summary.json")

    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(rows, handle, ensure_ascii=False, indent=2)

    fieldnames = [
        "id",
        "question",
        "ground_truth",
        "answer",
        "status",
        "latency_ms",
        "conversation_id",
        "context_count",
        "hit_at_k",
        "mrr",
        "faithfulness",
        "answer_relevancy",
        "context_recall",
        "context_precision",
        "retrieved_atomic_point_ids",
        "contexts",
        "error",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})

    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)


def _build_summary(rows: list[dict[str, Any]], ragas_summary: dict[str, float], ragas_note: str | None) -> dict[str, Any]:
    successful = [row for row in rows if row["status"] == "ok"]
    latency_values = [row["latency_ms"] for row in successful]
    hit_values = [row["hit_at_k"] for row in successful if row["hit_at_k"] is not None]
    mrr_values = [row["mrr"] for row in successful if row["mrr"] is not None]

    summary: dict[str, Any] = {
        "total_cases": len(rows),
        "successful_cases": len(successful),
        "error_cases": len(rows) - len(successful),
        "success_rate": round(len(successful) / len(rows), 4) if rows else 0.0,
        "avg_latency_ms": round(statistics.mean(latency_values), 2) if latency_values else 0.0,
        "retrieval_hit_rate": round(statistics.mean(hit_values), 4) if hit_values else None,
        "retrieval_mrr": round(statistics.mean(mrr_values), 4) if mrr_values else None,
    }
    summary.update(ragas_summary)
    if ragas_note:
        summary["ragas_note"] = ragas_note
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run retrieval metrics and optional Ragas metrics for the chatbot RAG flow."
    )
    parser.add_argument("--base-url", default=os.environ.get("EVAL_BASE_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--auth-token", default=os.environ.get("EVAL_AUTH_TOKEN", ""))
    parser.add_argument("--cases", default="tools/eval/rag_cases.jsonl")
    parser.add_argument("--rag-limit", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--skip-ragas", action="store_true")
    parser.add_argument("--out", default="tools/eval/results/ragas_latest")
    args = parser.parse_args()

    cases = _load_cases(Path(args.cases))
    rows = run_eval(
        base_url=args.base_url,
        auth_token=args.auth_token,
        cases=cases,
        rag_limit=args.rag_limit,
        timeout_s=args.timeout,
    )

    ragas_summary: dict[str, float] = {}
    ragas_note: str | None = None
    if not args.skip_ragas:
        ragas_summary, rows, ragas_note = _try_run_ragas(rows)

    summary = _build_summary(rows, ragas_summary, ragas_note)
    _write_outputs(Path(args.out), rows, summary)

    print("=== RAG Evaluation Summary ===")
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
