from pydantic import BaseModel


class CreateAPRequest(BaseModel):
    type : str
    name : str
    description : str
    examples : str
    level : str
    popularity : float
    