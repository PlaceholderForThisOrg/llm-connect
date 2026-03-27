from fastapi import BackgroundTasks
from llm_connect import logger


class AEvaluator:
    def __init__(self):
        None

    def run(self, content: str, engine: BackgroundTasks):
        engine.add_task(self._evaluate, content=content, session_id = "1")

    def _evaluate(self, content: str, session_id : str):
        # TODO: Implement the evaluation to extract
        # the performance on the current atomic points
        # [1] Extract the current performance based
        # on the atomic points
        # [2] Calculate the performance score
        # threshold for BKT
        logger.info(f"💬: {content}")