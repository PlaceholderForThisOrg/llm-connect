from llm_connect.repositories.SessionRepository import SessionRepository


class Evaluator:
    def __init__(
        self,
        ses_repo: SessionRepository,
    ):
        self.ses_repo = ses_repo

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

        # i = {
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
        # p = interaction["pass"]

        points = interaction["points"]

        for point in points:
            # Run the MasteryEngine
            # to update the mastery
            # p = True
            pass
