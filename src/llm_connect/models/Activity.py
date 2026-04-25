from typing import Dict, List

from beanie import Document
from pydantic import BaseModel


class Task(BaseModel):
    id: str
    atomic_points: List[str]
    next_possibles: List[str]


class GenerateTask(Task):
    prompt: str


class Metadata(BaseModel):
    type: str
    title: str
    description: str
    general_difficulty: str
    estimated_time: str


class RolePlayMetadata(Metadata):
    location: str
    npc_name: str
    npc_role: str
    npc_personality: str
    general_goal: str


class Activity(Document):
    id: str
    metadata: Metadata
    start_goals: List[str]
    tasks: Dict[str, Task]
