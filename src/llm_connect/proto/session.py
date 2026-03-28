import json
from datetime import UTC, datetime, timezone
from pathlib import Path

from llm_connect import logger

now = datetime.now(UTC)

interaction = {"timestamp": now, "of": "LEARNER", "type": "MESSAGE"}  # AcTIVITY  #


session = {
    "activity_id": "activity_002",
    "checkpoint": "0",
    "history": [],
    "time_start": datetime.now(timezone.utc).timestamp(),
    "status": "RUNNING",  # PAUSED # DONE
}


def sync_session():
    logger.info("🥐 Session is synchronized")
    p = Path(__file__).resolve().parent / "runtime_db" / "session.json"
    with open(p, "w") as f:
        json.dump(session, f)


sync_session()
