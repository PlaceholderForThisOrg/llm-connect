from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

from llm_connect.configs.llm import ENDPOINT, TOKEN

client = ChatCompletionsClient(
    endpoint=ENDPOINT,
    credential=AzureKeyCredential(TOKEN),
)
