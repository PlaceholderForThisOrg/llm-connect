from fastapi import APIRouter
from llm_connect.schemas import chat_schema
from ollama import chat, ChatResponse

router = APIRouter(prefix="/api/v1/llm", tags=["LLM"])


@router.post("/generate")
def generate(request: chat_schema.ChatRequest):
    response: ChatResponse = chat(
        model="phi3.5:3.8b",
        messages=[
            {
                "role": "user",
                "content": request.message,
            },
        ],
    )
    return chat_schema.ChatResponse(message=response["message"]["content"])
