# Simple LLM Evaluation (Keyword + Latency)

## 1) Prepare
- Start backend service.
- Prepare token if your endpoint requires auth.
- Adjust test cases in `tools/eval/sample_cases.jsonl`.

## 2) Run
Example for conversation message endpoint:

```bash
uv run python tools/eval/simple_llm_eval.py \
  --base-url http://127.0.0.1:8000 \
  --endpoint /api/v1/me/conversations/<conversation_id>/messages/ \
  --method POST \
  --query-field content \
  --response-field content \
  --headers '{"Authorization":"Bearer <your_token>"}'
```

If your endpoint needs extra payload fields, pass them using `--static-payload`.

Example:

```bash
--static-payload '{"sessionId":"<session_id>"}'
```

## 3) Output
- Summary is printed in terminal.
- Detailed files:
  - `tools/eval/results/latest.json`
  - `tools/eval/results/latest.csv`

## 4) Metrics to report
- `Avg keyword score` (0-1): rough correctness.
- `Avg latency (ms)`: response speed.
- `Errors`: reliability.

This method is intentionally simple for quick thesis/report usage.
