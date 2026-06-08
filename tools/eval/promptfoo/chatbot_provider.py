import os
from typing import Any

import httpx


def _get_config(options: dict[str, Any]) -> dict[str, Any]:
    return options.get("config", {}) if options else {}


def _pick_base_url(config: dict[str, Any]) -> str:
    return str(
        config.get("baseUrl")
        or os.environ.get("EVAL_BASE_URL")
        or "http://127.0.0.1:8000"
    ).rstrip("/")


def _pick_token(config: dict[str, Any]) -> str:
    return str(config.get("authToken") or os.environ.get("EVAL_AUTH_TOKEN") or "")


def _pick_conversation_id(
    config: dict[str, Any],
    context: dict[str, Any],
) -> str | None:
    vars_dict = context.get("vars", {}) if context else {}
    return (
        vars_dict.get("conversation_id")
        or config.get("conversationId")
        or os.environ.get("EVAL_CONVERSATION_ID")
    )


def _headers(token: str) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _create_conversation(client: httpx.Client, token: str) -> str:
    response = client.post(
        "/api/v1/me/conversations/",
        headers=_headers(token),
    )
    response.raise_for_status()
    body = response.json()
    conversation_id = body.get("id")
    if not conversation_id:
        raise ValueError("Conversation creation succeeded but no 'id' was returned.")
    return str(conversation_id)


def _chat(
    client: httpx.Client,
    token: str,
    conversation_id: str,
    prompt: str,
) -> dict[str, Any]:
    response = client.post(
        f"/api/v1/me/conversations/{conversation_id}/messages/",
        json={"content": prompt},
        headers=_headers(token),
    )
    response.raise_for_status()
    return response.json()


def _retrieve_context(
    client: httpx.Client,
    prompt: str,
    rag_limit: int,
) -> list[dict[str, Any]]:
    response = client.get(
        "/api/v1/atomic-points/rag/search",
        params={"q": prompt, "limit": rag_limit},
    )
    response.raise_for_status()
    body = response.json()
    return body if isinstance(body, list) else []


def call_api(prompt: str, options: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    config = _get_config(options)
    base_url = _pick_base_url(config)
    token = _pick_token(config)
    rag_limit = int(config.get("ragLimit", 5))

    timeout_s = float(config.get("timeoutSeconds", 60))
    with httpx.Client(base_url=base_url, timeout=timeout_s) as client:
        conversation_id = _pick_conversation_id(config, context)
        if not conversation_id:
            conversation_id = _create_conversation(client, token)

        chat_body = _chat(client, token, conversation_id, prompt)
        rag_hits = _retrieve_context(client, prompt, rag_limit)

    return {
        "output": {
            "answer": chat_body.get("content", ""),
            "context": rag_hits,
            "conversation_id": conversation_id,
            "raw_response": chat_body,
        }
    }
