from llm_connect.repositories.SessionRepository import SessionRepository
from llm_connect.services.core.MasteryEngine import MasteryEngine


class Evaluator:
    def __init__(
        self,
        ses_repo: SessionRepository,
        m_e: MasteryEngine,
    ):
        self.ses_repo = ses_repo
        self.m_e = m_e

    # NOTE: Language evaluator
    # language's evaluation
    # interaction -> performace
    def run(self, interaction):
        # FIXME: simple
        # pass -> update all current
        # atomic points
        # fail -> update all current
        # atomic points
        # TODO: Implement the real pipeline here
        # store the performance
        # use that performance to update the mastery

        # i = {
        #     "learner_id" : "id"
        #     "session_id": "id",
        #     "type": "MESSAGE",
        #     "content": "Something else",
        #     "goal": "",
        #     "pass": False,
        #     # time to solve
        #     # ...
        #     "points": ["ap_0", "ap_1"],
        # }

        # true or false
        # true -> curr_goal
        p = interaction["pass"]
        learner_id = interaction["learner_id"]

        points = interaction["points"]

        for point in points:
            # Run the MasteryEngine
            # to update the mastery
            # p = True
            self.m_e.update(learner_id, point, p)
