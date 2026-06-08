# Intent Evaluation Report

## Overall

| Metric | Value |
| --- | ---: |
| Total cases | 40 |
| Successful cases | 40 |
| Intent accuracy | 0.93 |
| Scope accuracy | 1.00 |
| Latency p50 (ms) | 563.64 |
| Latency p95 (ms) | 3170.93 |
| Latency p99 (ms) | 4341.45 |
| Avg latency (ms) | 965.04 |

## By Intent

| Intent | Cases | Intent Accuracy | Scope Accuracy | Average Latency (ms) |
| --- | ---: | ---: | ---: | ---: |
| correction | 10 | 0.90 | 1.00 | 1320.05 |
| explanation | 10 | 1.00 | 1.00 | 791.64 |
| flashcard | 10 | 0.90 | 1.00 | 663.22 |
| task_help | 10 | 0.90 | 1.00 | 1085.27 |

## Confusion Matrix

```json
{
  "correction": {
    "correction": 9,
    "explanation": 1
  },
  "explanation": {
    "explanation": 10
  },
  "flashcard": {
    "flashcard": 9,
    "task_help": 1
  },
  "task_help": {
    "task_help": 9,
    "explanation": 1
  }
}
```