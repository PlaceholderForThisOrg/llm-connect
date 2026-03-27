from pydantic import BaseModel

class Interaction(BaseModel):
    session_id : str
    type : str = None
    of : str = None
    content : str
    timestamp : str = None