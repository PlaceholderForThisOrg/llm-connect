import json
from datetime import UTC, datetime, timezone
from pathlib import Path

from llm_connect import logger

now = datetime.now(UTC)

interaction = {"timestamp": now, "of": "LEARNER", "type": "MESSAGE"}  # AcTIVITY  #


session_v2 = {
    "session_id": "session_002",
    "activity_id": "activity_002",
    "current_goal": "0",  # pointer to the current goal that requires
    # the learner to complete
    "history": [],
    "time_start": datetime.now(timezone.utc).timestamp(),
    "status": "RUNNING",  # PAUSED # DONE
}


def sync_session():
    logger.info("🥐 Session is synchronized")
    p = Path(__file__).resolve().parent.parent / "runtime_db" / "session_v2.json"
    with open(p, "w") as f:
        json.dump(session_v2, f, indent=4)


sync_session()
