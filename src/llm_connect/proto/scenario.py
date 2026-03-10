import json
from pathlib import Path

JSON = Path(__file__).resolve().parent.parent

with open(JSON / "json" / "scenario_template" / "1.json") as file:
    scenario_template = json.load(file)

scenario = {"id": 1, "messages": [], "state": "BEGINNING"}
