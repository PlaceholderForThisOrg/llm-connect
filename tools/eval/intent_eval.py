import argparse
import asyncio
import csv
import json
import os
import statistics
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI

from llm_connect.configs.llm import ENDPOINT, GPT4OMINI
from llm_connect.services.core.Companion import Brain, Intent, Scope
from llm_connect.services.immerse.PromptBuilder import PromptBuilder


def _load_cases(path: Path) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                case = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at line {line_no}: {exc}") from exc
            if "message" not in case or "expected_intent" not in case:
                raise ValueError(
                    f"Case at line {line_no} must include 'message' and 'expected_intent'."
                )
            cases.append(case)
    return cases


def _resolve_token(cli_token: str | None) -> str:
    if cli_token:
        return cli_token
    for name in [
        "GITHUB_MODEL_TOKEN_GPT4OMINI",
        "GITHUB_MODEL_TOKEN",
        "OPENAI_API_KEY",
    ]:
        value = os.environ.get(name)
        if value:
            return value
    return ""


def _normalize_intent(value: str) -> str:
    return str(value).strip().lower()


def _normalize_scope(value: str | None, has_active_task: bool) -> str:
    if value:
        return str(value).strip().lower()
    return Scope.SESSION_TASK.value if has_active_task else Scope.GLOBAL.value


def _safe_div(num: float, den: float) -> float:
    return round(num / den, 4) if den else 0.0


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return round(values[0], 2)
    ordered = sorted(values)
    index = (len(ordered) - 1) * percentile
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    weight = index - lower
    result = ordered[lower] * (1 - weight) + ordered[upper] * weight
    return round(result, 2)


def _build_client(token: str, base_url: str) -> AsyncOpenAI | None:
    if not token:
        return None
    return AsyncOpenAI(base_url=base_url, api_key=token)


async def _predict_intent(
    *,
    brain: Brain,
    message: str,
    has_active_task: bool,
    history: list[str],
    mode: str,
) -> tuple[str, str, float, str]:
    rule_result = brain._rule_based_intent(message, has_active_task)  # noqa: SLF001

    if mode == "rule":
        if rule_result is None:
            return (
                Intent.OTHER.value,
                Scope.SESSION_TASK.value if has_active_task else Scope.GLOBAL.value,
                0.0,
                "fallback_other",
            )
        return (
            rule_result.intent.value,
            rule_result.scope.value,
            rule_result.confidence,
            "rule",
        )

    if rule_result is not None:
        return (
            rule_result.intent.value,
            rule_result.scope.value,
            rule_result.confidence,
            "rule",
        )

    result = await brain.detect_intent(
        message=message,
        has_active_task=has_active_task,
        history=history,
    )
    source = "llm" if result.confidence > 0.3 else "fallback_other"
    return result.intent.value, result.scope.value, result.confidence, source


async def run_eval(
    *,
    cases: list[dict[str, Any]],
    model: str,
    token: str,
    base_url: str,
    mode: str,
) -> list[dict[str, Any]]:
    prompt_builder = PromptBuilder()
    client = _build_client(token, base_url)
    brain = Brain(client, pb=prompt_builder)

    rows: list[dict[str, Any]] = []
    for case in cases:
        history = case.get("history", [])
        if not isinstance(history, list):
            history = [str(history)]
        has_active_task = bool(case.get("has_active_task", False))
        expected_intent = _normalize_intent(case["expected_intent"])
        expected_scope = _normalize_scope(case.get("expected_scope"), has_active_task)

        t0 = time.perf_counter()
        try:
            predicted_intent, predicted_scope, confidence, source = await _predict_intent(
                brain=brain,
                message=str(case["message"]),
                has_active_task=has_active_task,
                history=[str(item) for item in history],
                mode=mode,
            )
            latency_ms = (time.perf_counter() - t0) * 1000
            rows.append(
                {
                    "id": case.get("id", ""),
                    "message": case["message"],
                    "group": case.get("group", ""),
                    "has_active_task": has_active_task,
                    "expected_intent": expected_intent,
                    "predicted_intent": predicted_intent,
                    "intent_correct": predicted_intent == expected_intent,
                    "expected_scope": expected_scope,
                    "predicted_scope": predicted_scope,
                    "scope_correct": predicted_scope == expected_scope,
                    "confidence": round(float(confidence), 4),
                    "latency_ms": round(latency_ms, 2),
                    "classifier_source": source if mode == "rule" or client else source,
                    "status": "ok",
                }
            )
        except Exception as exc:  # noqa: BLE001
            latency_ms = (time.perf_counter() - t0) * 1000
            rows.append(
                {
                    "id": case.get("id", ""),
                    "message": case["message"],
                    "group": case.get("group", ""),
                    "has_active_task": has_active_task,
                    "expected_intent": expected_intent,
                    "predicted_intent": "",
                    "intent_correct": False,
                    "expected_scope": expected_scope,
                    "predicted_scope": "",
                    "scope_correct": False,
                    "confidence": 0.0,
                    "latency_ms": round(latency_ms, 2),
                    "classifier_source": "error",
                    "status": "error",
                    "error": str(exc),
                }
            )

    _ = model
    return rows


def _build_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    successful = [row for row in rows if row["status"] == "ok"]
    latencies = [float(row["latency_ms"]) for row in successful]
    intent_hits = sum(1 for row in successful if row["intent_correct"])
    scope_hits = sum(1 for row in successful if row["scope_correct"])

    per_intent: dict[str, dict[str, Any]] = {}
    grouped_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in successful:
        grouped_rows[row["expected_intent"]].append(row)

    for intent, intent_rows in sorted(grouped_rows.items()):
        per_intent[intent] = {
            "count": len(intent_rows),
            "intent_accuracy": _safe_div(
                sum(1 for row in intent_rows if row["intent_correct"]),
                len(intent_rows),
            ),
            "scope_accuracy": _safe_div(
                sum(1 for row in intent_rows if row["scope_correct"]),
                len(intent_rows),
            ),
            "avg_latency_ms": round(
                statistics.mean(float(row["latency_ms"]) for row in intent_rows), 2
            ),
        }

    confusion: dict[str, dict[str, int]] = defaultdict(dict)
    for row in successful:
        expected = row["expected_intent"]
        predicted = row["predicted_intent"]
        confusion[expected][predicted] = confusion[expected].get(predicted, 0) + 1

    classifier_sources = Counter(row["classifier_source"] for row in successful)

    return {
        "total_cases": total,
        "successful_cases": len(successful),
        "error_cases": total - len(successful),
        "intent_accuracy": _safe_div(intent_hits, len(successful)),
        "scope_accuracy": _safe_div(scope_hits, len(successful)),
        "avg_latency_ms": round(statistics.mean(latencies), 2) if latencies else 0.0,
        "latency_p50_ms": _percentile(latencies, 0.50),
        "latency_p95_ms": _percentile(latencies, 0.95),
        "latency_p99_ms": _percentile(latencies, 0.99),
        "classifier_sources": dict(classifier_sources),
        "per_intent": per_intent,
        "confusion_matrix": {key: value for key, value in sorted(confusion.items())},
    }


def _render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Intent Evaluation Report",
        "",
        "## Overall",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Total cases | {summary['total_cases']} |",
        f"| Successful cases | {summary['successful_cases']} |",
        f"| Intent accuracy | {summary['intent_accuracy']:.2f} |",
        f"| Scope accuracy | {summary['scope_accuracy']:.2f} |",
        f"| Latency p50 (ms) | {summary['latency_p50_ms']:.2f} |",
        f"| Latency p95 (ms) | {summary['latency_p95_ms']:.2f} |",
        f"| Latency p99 (ms) | {summary['latency_p99_ms']:.2f} |",
        f"| Avg latency (ms) | {summary['avg_latency_ms']:.2f} |",
        "",
        "## By Intent",
        "",
        "| Intent | Cases | Intent Accuracy | Scope Accuracy | Average Latency (ms) |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for intent, values in summary["per_intent"].items():
        lines.append(
            f"| {intent} | {values['count']} | {values['intent_accuracy']:.2f} | "
            f"{values['scope_accuracy']:.2f} | {values['avg_latency_ms']:.2f} |"
        )

    lines.extend(
        [
            "",
            "## Confusion Matrix",
            "",
            "```json",
            json.dumps(summary["confusion_matrix"], ensure_ascii=False, indent=2),
            "```",
        ]
    )
    return "\n".join(lines)


def _write_outputs(prefix: Path, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    prefix.parent.mkdir(parents=True, exist_ok=True)

    json_path = prefix.with_suffix(".json")
    csv_path = prefix.with_suffix(".csv")
    summary_path = prefix.with_suffix(".summary.json")
    md_path = prefix.with_suffix(".report.md")

    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(rows, handle, ensure_ascii=False, indent=2)

    fieldnames = [
        "id",
        "message",
        "group",
        "has_active_task",
        "expected_intent",
        "predicted_intent",
        "intent_correct",
        "expected_scope",
        "predicted_scope",
        "scope_correct",
        "confidence",
        "latency_ms",
        "classifier_source",
        "status",
        "error",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})

    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)

    with md_path.open("w", encoding="utf-8") as handle:
        handle.write(_render_markdown(summary))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate the chatbot intent classifier using the existing Companion intent pipeline."
    )
    parser.add_argument("--cases", default="tools/eval/intent_cases.jsonl")
    parser.add_argument("--out", default="tools/eval/results/intent_latest")
    parser.add_argument("--mode", choices=["rule", "full"], default="rule")
    parser.add_argument("--model", default=GPT4OMINI)
    parser.add_argument("--base-url", default=ENDPOINT)
    parser.add_argument("--api-key", default=None)
    args = parser.parse_args()

    token = _resolve_token(args.api_key)
    if args.mode == "full" and not token:
        raise ValueError(
            "Full mode requires an API key. Set --api-key or one of "
            "GITHUB_MODEL_TOKEN_GPT4OMINI, GITHUB_MODEL_TOKEN, OPENAI_API_KEY."
        )

    cases = _load_cases(Path(args.cases))
    rows = asyncio.run(
        run_eval(
            cases=cases,
            model=args.model,
            token=token,
            base_url=args.base_url,
            mode=args.mode,
        )
    )
    summary = _build_summary(rows)
    _write_outputs(Path(args.out), rows, summary)

    print("=== Intent Evaluation Summary ===")
    for key in [
        "total_cases",
        "successful_cases",
        "error_cases",
        "intent_accuracy",
        "scope_accuracy",
        "avg_latency_ms",
        "latency_p50_ms",
        "latency_p95_ms",
        "latency_p99_ms",
    ]:
        print(f"{key}: {summary[key]}")


if __name__ == "__main__":
    main()
