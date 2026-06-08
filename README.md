# My Companion Backend Service

This is the backend service for **My Companion**.

## 🚀 Getting Started

Follow these steps to run the service locally:

### 1. Create environment file

Create a `.env.development` file in the root directory.

### 2. Configure environment variables

Copy the required variables from `.env.example` and provide the appropriate values in `.env.development`.

### 3. Run the service

Start the backend using the following command:

```bash
uv run python -m llm_connect.main



docker compose up postgres mongodb -d
docker compose run --rm flyway
uv run python -m llm_connect.main
```

### 4. Eval AI

Intent eval:

```powershell
$env:GITHUB_MODEL_TOKEN="token"
.venv\Scripts\python.exe tools/eval/intent_eval.py --mode full
```

Simple response eval:

```powershell
$env:EVAL_ACCESS_TOKEN="token"
$env:EVAL_CONVERSATION_ID="conversation_id"

@'
import os
from pathlib import Path
from tools.eval.simple_llm_eval import _load_cases, run_eval, _write_outputs, _print_summary

rows = run_eval(
    base_url='http://127.0.0.1:8000',
    endpoint=f"/api/v1/me/conversations/{os.environ['EVAL_CONVERSATION_ID']}/messages/",
    method='POST',
    cases=_load_cases(Path('tools/eval/sample_cases.jsonl')),
    query_field='content',
    response_field='content',
    static_payload={},
    headers={'Authorization': f"Bearer {os.environ['EVAL_ACCESS_TOKEN']}"},
    timeout_s=45.0,
)
json_path, csv_path = _write_outputs(Path('tools/eval/results/latest'), rows)
_print_summary(rows)
print(f'JSON results: {json_path}')
print(f'CSV results : {csv_path}')
'@ | .venv\Scripts\python.exe -
```
