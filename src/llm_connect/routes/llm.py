from azure.ai.inference.models import SystemMessage, UserMessage
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from llm_connect.clients.llm import client
from llm_connect.configs import llm
from llm_connect.schemas import chat_schema

router = APIRouter(prefix="/api/v1/companion", tags=["Companion"])


@router.post("/chat")
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


@router.post("/chat-stream")
def generate_stream(request: chat_schema.ChatRequest):

    def stream():
        response = client.complete(
            messages=[
                SystemMessage("You are an English companion"),
                UserMessage(request.message),
            ],
            temperature=1.0,
            top_p=1.0,
            model=llm.MODEL,
            stream=True,
        )

        for chunk in response:
            if chunk and chunk.choices:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    yield delta

        yield "[END]"

    return StreamingResponse(stream(), media_type="text/event-stream")
