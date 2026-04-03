from fastapi import BackgroundTasks

from llm_connect import logger


class Analyzer:
    def __init__(self):
        None

    def run(self, input: str, engine: BackgroundTasks):
        # TODO Implement the evaluation pipeline here
        # FIXME Refactor this pipeline later on to another service
        # after prototyping the evaluation pipeline

        engine.add_task(self._evaluate, input=input)

    def _evaluate(self, input: str):
        # TODO Implement the evaluation pipeline here
        logger.info(f"💬: {input}")
