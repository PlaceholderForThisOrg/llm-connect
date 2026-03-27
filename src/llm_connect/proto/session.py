from datetime import UTC, datetime

now = datetime.now(UTC)

interaction = {"timestamp": now, "of": "LEARNER", "type": "MESSAGE"}  # AcTIVITY  #


session = {
    "activity_id": "activity_002",
    "checkpoint": "0",
    "history": [],
    "time_start": now,
    "status": "RUNNING",  # PAUSED
}
