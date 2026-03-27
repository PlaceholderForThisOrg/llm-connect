from datetime import datetime, timezone

from fastapi import BackgroundTasks

from llm_connect import logger
from llm_connect.proto import scenario, scenario_template
from llm_connect.services.analyzer.Analyzer import Analyzer
from llm_connect.services.core.aevaluator import AEvaluator
from llm_connect.services.immerse import Actor, Evaluator, PromptBuilder
from llm_connect.proto.session import session


class Orchestrator:
    def __init__(
        self,
        evaluator: Evaluator,
        actor: Actor,
        prompt_builder: PromptBuilder,
        analyzer: Analyzer,
        aevaluator : AEvaluator
    ):
        self.evaluator = evaluator
        self.actor = actor
        self.prompt_builder = prompt_builder
        self.analyzer = analyzer
        self.aevaluator = aevaluator

    async def start(
        self,
        scenario_id: int,
        input: str,
        engine: BackgroundTasks,
    ):
        # TODO: The orchestrator is run on each interaction between
        # the learner and the system
        
        # TODO: Store the current interaction first
        # 1. Create the interaction object
        timestamp = datetime.now(timezone.utc).timestamp()
        interaction = {
            "id" : "0",
            "type" : "MESSAGE",
            "of" : "LEARNER",
            "content" : input,
            "timestamp" : timestamp
        }
        session["history"].append (interaction)
        
        # TODO: Run the evaluator to extract the performance
        # on the expected atomic points
        # Optionally extract the errors in-place
        self.aevaluator.run(input, engine)
        
        # TODO: Activity, check whether the current checkpoint
        # is good to move
        
        # [1] Get the current state
        
        
        
        
        
        
        # [1] The orchestrator receives the message from the learner
        # store that message into the scenario object
        scenario["messages"].append({"role": "learner", "content": input})
        # [2] Use that message/history to ask for the current state from the evaluator
        # get the result

        # FIXME yield to end the orchestrator
        # and a loop of yield on the stream of the response of the LLM
        state = scenario["state"]
        if state == "END":
            yield "You have successfully finished this scenario, good job."
        else:
            logger.info(f"Current state: {scenario["state"]}")

            state = await self.evaluator.next_state(input)

            # [2.1] Use the state to update the current state
            if state is True:
                # Move the scenario to the next state
                # check for the end state
                if scenario["index"] == len(scenario_template["states"]):
                    # conversation has done
                    yield "nothing"

                scenario["index"] += 1
                scenario["state"] = scenario_template["states"][scenario["index"]][
                    "name"
                ]

            # [3] Use that result to build the second prompt for the actor
            # send to the actor LLM

            logger.info(f"Current scenario: {scenario}")

            # [4] Stream the result back to the learner/store the message
            async for token in self.actor.say(input):
                yield token

        self.analyzer.run(input, engine)
