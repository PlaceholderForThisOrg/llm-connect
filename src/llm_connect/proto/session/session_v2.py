from datetime import UTC, datetime, timezone

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
