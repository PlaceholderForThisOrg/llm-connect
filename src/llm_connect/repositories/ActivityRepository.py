from llm_connect.proto.activity import activity_v2

class ActivityRepository:
    def __init__(self):
        pass
    
    def get_activity_by_id(self, activity_id : str):
        # FIXME: prototype only
        return activity_v2
    
    
    def get_checkpoint_by_id(self, activity_id, checkpoint_id):
        # FIXME: prototype only - in-memory
        return activity_v2["checkpoints"][activity_id]