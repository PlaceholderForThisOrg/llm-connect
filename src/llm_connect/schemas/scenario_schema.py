from pydantic import BaseModel


class ImmerseScenarioRequest(BaseModel):
    scenario_id: int
    message: str
