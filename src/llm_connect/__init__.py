from pathlib import Path

from dotenv import load_dotenv

from llm_connect.logger import logger

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_REPO_ROOT / ".env.development", verbose=True)
load_dotenv(_REPO_ROOT / ".env", verbose=True)


__all__ = ["logger"]
