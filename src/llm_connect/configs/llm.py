import os

ENDPOINT = "https://models.github.ai/inference"
MODEL = "openai/gpt-4.1"


def TOKEN():
    return os.environ["GITHUB_MODEL_TOKEN"]
