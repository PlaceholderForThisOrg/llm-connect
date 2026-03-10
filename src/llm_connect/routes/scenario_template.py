from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/scenario-templates")


@router.post(
    path="/",
    response_model=None,
    description="Create a scenario template",
)
async def create_scenario_template():
    None
