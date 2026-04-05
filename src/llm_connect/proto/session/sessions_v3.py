from datetime import datetime, timezone

# dict of session
sessions_v3 = {
    "random": {
        "session_id": "random",
        "activity_id": "activity_002",
        "current_goal": "0",  # pointer to the current goal that requires
        # the learner to complete
        "history": [],
        "time_start": datetime.now(timezone.utc).timestamp(),
        "status": "RUNNING",  # PAUSED # DONE
    }
}
