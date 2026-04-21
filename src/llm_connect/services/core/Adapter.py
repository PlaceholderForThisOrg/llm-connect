from llm_connect.repositories.ActivityRepository import ActivityRepository
from llm_connect.repositories.LearnerRepository import LearnerRepository


class Adapter:
    def __init__(
        self,
        l_r: LearnerRepository,
        a_r: ActivityRepository,
    ):
        self.l_r = l_r
        self.a_r = a_r

    def next(self, learner_id: str, t: str):
        # TODO: Based on the current mastery levels
        # recommend ...
        # FIXME: Should be run periodically
        # prototype, run on the fly

        # return a list of activity_id?

        # logic to check for
        # preference
        # poor atomic points
        #

        if t == "ACTIVITY":
            return self.next_activities()

        elif t == "NEWS":
            return self.next_others()

    def next_activities(self):
        return self.a_r.get_activities()

    def next_others(self):
        return "Here is other activities"
