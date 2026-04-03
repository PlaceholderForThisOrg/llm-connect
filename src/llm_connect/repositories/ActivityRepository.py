from llm_connect.proto.activity.activity_v4 import activity_v4


class ActivityRepository:
    def __init__(self):
        pass

    def get_activity_by_id(self, activity_id: str):
        # FIXME: prototype only
        return activity_v4

    def get_interaction_by_id(self, activity_id: str, interaction_id: str):
        return activity_v4["interactions"][interaction_id]

    def get_checkpoint_by_id(self, activity_id, checkpoint_id):
        # FIXME: prototype only - in-memory
        return activity_v4["checkpoints"][checkpoint_id]

    def get_goal_by_id(self, activity_id, goal_id):
        return activity_v4["goals"][goal_id]
