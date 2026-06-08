# Evaluation Toolkit

This project now has 3 evaluation layers for the chatbot:

1. `simple_llm_eval.py`
Quick smoke test for latency, errors, and keyword coverage.

2. `promptfoo`
End-to-end regression evaluation for answer quality and RAG grounding.

3. `ragas_eval.py`
RAG-focused evaluation for retrieval metrics plus optional Ragas metrics.

4. `intent_eval.py`
Intent classification evaluation using the same `Companion` intent pipeline as the app.

## 1) Quick smoke test

Use this when you want fast numbers for:
- average latency
- average keyword score
- error count

Example:

```bash
uv run python tools/eval/simple_llm_eval.py \
  --base-url http://127.0.0.1:8000 \
  --endpoint /api/v1/me/conversations/<conversation_id>/messages/ \
  --method POST \
  --query-field content \
  --response-field content \
  --headers '{"Authorization":"Bearer <your_token>"}'
```

Outputs:
- `tools/eval/results/latest.json`
- `tools/eval/results/latest.csv`

## 4) Intent evaluation

Use this when you want numbers for:
- intent classification accuracy
- scope accuracy (`global` vs `session_task`)
- average latency and p50/p95/p99
- per-intent breakdown for the 3 runtime modes used by `response_v3()`

Main files:
- `tools/eval/intent_eval.py`
- `tools/eval/intent_cases.jsonl`

Current focus intents:
- `task_help` -> `mode_task_help_v2()`
- `correction` -> classifier-only evaluation for now
- `explanation` -> `mode_explain()`
- `flashcard` -> `mode_flashcard()`

### Dataset fields

Each JSONL line can contain:

```json
{
  "id": "intent-1",
  "message": "Correct this sentence: She go to school every day.",
  "expected_intent": "correction",
  "expected_scope": "global",
  "has_active_task": false,
  "group": "grammar",
  "history": []
}
```

Required:
- `message`
- `expected_intent`

Optional:
- `expected_scope`
- `has_active_task`
- `group`
- `history`

The default sample dataset is intentionally focused on:
- the 3 intents with dedicated runtime branches in `Companion.response_v3()`
- `correction`, which is useful to track separately even though it currently
  falls through to the general branch at runtime

### Run

Rule-only mode:

```bash
uv run python tools/eval/intent_eval.py --mode rule
```

Full mode with LLM fallback:

```bash
uv run python tools/eval/intent_eval.py --mode full
```

Full mode requires one of:
- `GITHUB_MODEL_TOKEN_GPT4OMINI`
- `GITHUB_MODEL_TOKEN`
- `OPENAI_API_KEY`

Outputs:
- `tools/eval/results/intent_latest.json`
- `tools/eval/results/intent_latest.csv`
- `tools/eval/results/intent_latest.summary.json`
- `tools/eval/results/intent_latest.report.md`

## 2) Promptfoo for regression eval

Use this when you want repeatable test cases for:
- answer relevance
- factuality against expected answers
- context faithfulness
- context recall
- context relevance

Promptfoo is configured through:
- `tools/eval/promptfoo/promptfooconfig.rag.yaml`
- `tools/eval/promptfoo/chatbot_provider.py`

### Prepare

Set environment variables:

```bash
set EVAL_BASE_URL=http://127.0.0.1:8000
set EVAL_AUTH_TOKEN=<your_token>
set OPENAI_API_KEY=<judge_model_key>
```

If your system needs a fixed learner conversation, you can also set:

```bash
set EVAL_CONVERSATION_ID=<conversation_id>
```

If `EVAL_CONVERSATION_ID` is omitted, the provider creates a new conversation for each test.

### Run

```bash
npx promptfoo@latest eval -c tools/eval/promptfoo/promptfooconfig.rag.yaml
```

### What the provider does

For each test case it:
- creates a conversation if needed
- sends the user query to `/api/v1/me/conversations/{conversationId}/messages/`
- calls `/api/v1/atomic-points/rag/search`
- returns both `answer` and retrieved `context` to Promptfoo

This lets Promptfoo grade the final answer and the retrieved context separately.

## 3) Ragas + retrieval metrics

Use this when you want structured RAG metrics and retrieval statistics.

Main script:
- `tools/eval/ragas_eval.py`

Sample dataset:
- `tools/eval/rag_cases.jsonl`

### Install eval dependencies

```bash
uv sync --group eval
```

### Prepare

Set:

```bash
set EVAL_BASE_URL=http://127.0.0.1:8000
set EVAL_AUTH_TOKEN=<your_token>
set OPENAI_API_KEY=<judge_model_key>
```

### Run

```bash
uv run python tools/eval/ragas_eval.py \
  --base-url %EVAL_BASE_URL% \
  --auth-token %EVAL_AUTH_TOKEN%
```

Optional flags:

```bash
--cases tools/eval/rag_cases.jsonl
--rag-limit 5
--skip-ragas
--out tools/eval/results/ragas_latest
```

### Dataset fields

Each JSONL line can contain:

```json
{
  "id": "rag-q1",
  "question": "Explain the difference between present simple and present continuous.",
  "ground_truth": "Present simple is used for habits and routines. Present continuous is used for actions happening now or around now.",
  "expected_atomic_point_ids": ["uuid-1", "uuid-2"]
}
```

`expected_atomic_point_ids` is optional, but it is needed for retrieval metrics such as `Hit@k` and `MRR`.

### Metrics produced

Always available:
- `avg_latency_ms`
- `success_rate`
- `retrieval_hit_rate`
- `retrieval_mrr`

Available when Ragas is installed and configured:
- `faithfulness`
- `answer_relevancy`
- `context_precision`
- `context_recall`

Outputs:
- `<out>.json`
- `<out>.csv`
- `<out>.summary.json`

## Suggested thesis/report table

Recommended columns:
- `avg_latency_ms`
- `success_rate`
- `keyword_score`
- `faithfulness`
- `answer_relevancy`
- `context_precision`
- `context_recall`
- `retrieval_hit_rate`
- `retrieval_mrr`

This gives you one balanced table covering system speed, answer quality, and RAG quality.

For intent evaluation, recommended report tables:
- overall `intent_accuracy`, `scope_accuracy`, `latency_p50_ms`, `latency_p95_ms`, `latency_p99_ms`
- per-intent `count`, `intent_accuracy`, `scope_accuracy`, `avg_latency_ms`
