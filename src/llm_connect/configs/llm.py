import os

ENDPOINT = "https://models.github.ai/inference"
GPT41 = "openai/gpt-4.1"
GPT4OMINI = "openai/gpt-4o-mini"


def TOKEN_GPT41():
    return os.environ["GITHUB_MODEL_TOKEN_GPT41"]


def TOKEN_GPT4OMINI():
    return os.environ["GITHUB_MODEL_TOKEN_GPT4OMINI"]


def TOKEN():
    return os.environ["GITHUB_MODEL_TOKEN"]
