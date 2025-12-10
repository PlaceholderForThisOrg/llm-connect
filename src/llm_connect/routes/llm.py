from azure.ai.inference.models import SystemMessage, UserMessage
from fastapi import APIRouter

from llm_connect.clients.llm import client
from llm_connect.configs import llm
from llm_connect.schemas import chat_schema

router = APIRouter(prefix="/api/v1/llm", tags=["LLM"])


@router.post("/generate")
def generate(request: chat_schema.ChatRequest):
    response = client.complete(
        messages=[
            SystemMessage("You are an English companion"),
            UserMessage(request.message),
        ],
        temperature=1.0,
        top_p=1.0,
        model=llm.MODEL,
        stream=False,
    )
    return chat_schema.ChatResponse(message=response.choices[0].message.content)
