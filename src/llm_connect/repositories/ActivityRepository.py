from llm_connect.proto.activity import activity_v3


class ActivityRepository:
    def __init__(self):
        pass

    def get_activity_by_id(self, activity_id: str):
        # FIXME: prototype only
        return activity_v3

    def get_interaction_by_id(self, activity_id: str, interaction_id: str):
        return activity_v3["interactions"][interaction_id]

    def get_checkpoint_by_id(self, activity_id, checkpoint_id):
        # FIXME: prototype only - in-memory
        return activity_v3["checkpoints"][checkpoint_id]
