import json
import os

from llm_connect.proto.masteries_v1 import masteries_v1


class MasteryRepository:
    def __init__(self):
        self.file_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "../proto/runtime_db/masteries.json"
            )
        )

        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    masteries_v1.update(data)
            except Exception:
                pass

        # Initial sync to ensure file exists
        self.sync()

    def sync(self):
        """Write current mastery to file"""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(masteries_v1, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[sync error] {e}")

    def new_mastery(self, learner_id: str, ap_id: str):
        if ap_id in masteries_v1[learner_id]:
            return None

        else:
            # not in, initialize
            # FIXME: Just an estimation
            # of the mastery of the current
            # atomic point
            mastery = {
                # parameters
                "p_init": 0.3,
                "p_learn": 0.15,
                "p_guess": 0.3,
                "p_slip": 0.2,
                # initial mastery estimation
                "p_L": 0.3,
            }

            masteries_v1[learner_id][ap_id] = mastery
            self.sync()

    def get_mastery(
        self,
        learner_id: str,
        ap_id: str,
    ):
        if ap_id not in masteries_v1[learner_id]:
            self.new_mastery(learner_id, ap_id)
        return masteries_v1[learner_id][ap_id]

    def update_mastery(
        self,
        learner_id: str,
        ap_id: str,
        new_estimation: float,
    ):
        mastery = self.get_mastery(learner_id, ap_id)
        mastery["p_L"] = new_estimation

        self.sync()

        return mastery

    def get_all(
        self,
        learner_id: str,
    ):
        # object of mastery record
        mastery = masteries_v1[learner_id]
        return mastery
