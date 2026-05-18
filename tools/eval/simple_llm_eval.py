import argparse
import csv
import json
import statistics
import time
from pathlib import Path
from typing import Any

import httpx


def _get_by_path(data: Any, path: str) -> Any:
    current = data
    for part in path.split('.'):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def _load_cases(path: Path) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    with path.open('r', encoding='utf-8') as f:
        for line_no, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                cases.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f'Invalid JSONL at line {line_no}: {exc}') from exc
    return cases


def _build_payload(template: dict[str, Any], question: str, query_field: str) -> dict[str, Any]:
    payload = dict(template)
    payload[query_field] = question
    return payload


def _score_keywords(answer_text: str, expected_keywords: list[str]) -> float:
    if not expected_keywords:
        return 1.0
    lower_answer = answer_text.lower()
    hits = sum(1 for kw in expected_keywords if kw.lower() in lower_answer)
    return hits / len(expected_keywords)


def run_eval(
    base_url: str,
    endpoint: str,
    method: str,
    cases: list[dict[str, Any]],
    query_field: str,
    response_field: str,
    static_payload: dict[str, Any],
    headers: dict[str, str],
    timeout_s: float,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    with httpx.Client(base_url=base_url.rstrip('/'), timeout=timeout_s) as client:
        for case in cases:
            payload = _build_payload(static_payload, case['question'], query_field)
            t0 = time.perf_counter()
            try:
                if method == 'GET':
                    response = client.get(endpoint, params=payload, headers=headers)
                else:
                    response = client.post(endpoint, json=payload, headers=headers)

                latency_ms = (time.perf_counter() - t0) * 1000
                response.raise_for_status()
                body = response.json()
                raw_answer = _get_by_path(body, response_field)
                answer_text = raw_answer if isinstance(raw_answer, str) else json.dumps(raw_answer, ensure_ascii=False)

                keyword_score = _score_keywords(answer_text, case.get('expected_keywords', []))

                results.append(
                    {
                        'id': case.get('id', ''),
                        'question': case['question'],
                        'answer': answer_text,
                        'status': 'ok',
                        'http_status': response.status_code,
                        'latency_ms': round(latency_ms, 2),
                        'keyword_score': round(keyword_score, 3),
                    }
                )
            except Exception as exc:  # noqa: BLE001
                latency_ms = (time.perf_counter() - t0) * 1000
                results.append(
                    {
                        'id': case.get('id', ''),
                        'question': case['question'],
                        'answer': '',
                        'status': 'error',
                        'http_status': '',
                        'latency_ms': round(latency_ms, 2),
                        'keyword_score': 0.0,
                        'error': str(exc),
                    }
                )

    return results


def _write_outputs(output_prefix: Path, rows: list[dict[str, Any]]) -> tuple[Path, Path]:
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    json_path = output_prefix.with_suffix('.json')
    csv_path = output_prefix.with_suffix('.csv')

    with json_path.open('w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    fieldnames = [
        'id',
        'question',
        'answer',
        'status',
        'http_status',
        'latency_ms',
        'keyword_score',
        'error',
    ]

    with csv_path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            full_row = {k: row.get(k, '') for k in fieldnames}
            writer.writerow(full_row)

    return json_path, csv_path


def _print_summary(rows: list[dict[str, Any]]) -> None:
    total = len(rows)
    success = [r for r in rows if r['status'] == 'ok']
    errors = total - len(success)

    avg_latency = statistics.mean([r['latency_ms'] for r in success]) if success else 0.0
    avg_score = statistics.mean([r['keyword_score'] for r in success]) if success else 0.0

    print('=== Simple LLM Eval Summary ===')
    print(f'Total cases       : {total}')
    print(f'Successful calls  : {len(success)}')
    print(f'Errors            : {errors}')
    print(f'Avg latency (ms)  : {avg_latency:.2f}')
    print(f'Avg keyword score : {avg_score:.3f}')


def main() -> None:
    parser = argparse.ArgumentParser(description='Run simple keyword-based LLM evaluation over an HTTP endpoint.')
    parser.add_argument('--base-url', required=True, help='Example: http://127.0.0.1:8000')
    parser.add_argument('--endpoint', required=True, help='Example: /api/v1/me/conversations/{id}/messages/')
    parser.add_argument('--method', choices=['POST', 'GET'], default='POST')
    parser.add_argument('--cases', default='tools/eval/sample_cases.jsonl')
    parser.add_argument('--query-field', default='content', help='Field name to inject question into payload.')
    parser.add_argument('--response-field', default='content', help='Dot path to answer field in JSON response.')
    parser.add_argument('--static-payload', default='{}', help='JSON object string added to each request payload.')
    parser.add_argument('--headers', default='{}', help='JSON object string for custom headers, e.g. auth token.')
    parser.add_argument('--timeout', type=float, default=45.0)
    parser.add_argument('--out', default='tools/eval/results/latest', help='Output prefix path (without extension).')

    args = parser.parse_args()

    cases = _load_cases(Path(args.cases))
    static_payload = json.loads(args.static_payload)
    headers = json.loads(args.headers)

    rows = run_eval(
        base_url=args.base_url,
        endpoint=args.endpoint,
        method=args.method,
        cases=cases,
        query_field=args.query_field,
        response_field=args.response_field,
        static_payload=static_payload,
        headers=headers,
        timeout_s=args.timeout,
    )

    json_path, csv_path = _write_outputs(Path(args.out), rows)
    _print_summary(rows)
    print(f'JSON results: {json_path}')
    print(f'CSV results : {csv_path}')


if __name__ == '__main__':
    main()
