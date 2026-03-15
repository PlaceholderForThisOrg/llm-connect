from fastapi import BackgroundTasks

from llm_connect import logger


class Analyzer:
    def __init__(self):
        None

    def run(self, engine: BackgroundTasks):
        # TODO Implement the evaluation pipeline here

        def simple():
            logger.info("💬 finished")

        engine.add_task(simple)
