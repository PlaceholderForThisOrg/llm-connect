import math
from collections import defaultdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Set

from llm_connect.models import Activity, Learner
from llm_connect.models.AtomicPoint import AtomicPoint
from llm_connect.repositories.ActivityRepository import ActivityRepository
from llm_connect.repositories.AtomicPointRepository import AtomicPointRepository
from llm_connect.repositories.LearnerRepository import LearnerRepository
from llm_connect.repositories.MasteryRepository import MasteryRepository


class RelationType(str, Enum):
    PREREQUISITE = "prerequisite"
    SIMILAR = "similar"
    CONFUSABLE = "confusable"


class Adapter:
    def __init__(
        self,
        l_r: LearnerRepository,
        a_r: ActivityRepository,
        mastery_repo: MasteryRepository,
        ap_repo: AtomicPointRepository,
    ):
        self.l_r = l_r
        self.a_r = a_r

        self.learner_repo = l_r
        self.activity_repo = a_r
        self.mastery_repo = mastery_repo
        self.ap_repo = ap_repo

    async def recommend(learner_id: str):
        None

    def build_knowledge_state(
        self,
        learner: Learner,
        atomic_points: List[AtomicPoint],
    ) -> Dict[str, float]:
        """
        K[atomic_point_id] = probability learner knows it
        """
        K = {str(ap.id): ap.p_init for ap in atomic_points}

        for m in learner.mastery_records:
            K[str(m.atomic_point_id)] = m.p_l

        return K

    def build_graph(self, atomic_points: List[AtomicPoint]):
        prereq_map = defaultdict(set)
        similar_map = defaultdict(set)

        for ap in atomic_points:
            for r in ap.outgoing_relations:
                if r.relation_type == RelationType.PREREQUISITE:
                    prereq_map[str(r.to_id)].add(str(r.from_id))

                elif r.relation_type in [RelationType.SIMILAR, RelationType.CONFUSABLE]:
                    similar_map[str(r.from_id)].add(str(r.to_id))
                    similar_map[str(r.to_id)].add(str(r.from_id))

        return prereq_map, similar_map

    def classify(self, p: float):
        if p < 0.3:
            return "weak"
        elif p < 0.7:
            return "learning"
        return "mastered"

    def build_target_set(self, K, prereq_map, similar_map):
        T = defaultdict(float)

        for ap, p in K.items():
            c = self.classify(p)

            # A. weak → highest priority
            if c == "weak":
                T[ap] += 1.0

                # B. prerequisite gaps
                for pre in prereq_map.get(ap, []):
                    if K.get(pre, 0) < 0.7:
                        T[pre] += 0.8

            # C. reinforcement
            elif c == "learning":
                for sim in similar_map.get(ap, []):
                    T[sim] += 0.5

        # D. frontier (ready to learn)
        for ap in K:
            if K[ap] < 0.3:
                prereqs = prereq_map.get(ap, [])
                if all(K.get(p, 0) >= 0.7 for p in prereqs):
                    T[ap] += 0.6

        return T

    def extract_activity_points(self, activity: Activity) -> Set[str]:
        points = set()

        for task in activity.tasks.values():
            for ap in task.atomic_points:
                points.add(ap)

        return points

    def difficulty_to_float(self, level: str) -> float:
        return {
            "beginner": 0.2,
            "elementary": 0.4,
            "intermediate": 0.6,
            "advanced": 0.85,
            "B1": 0.2,
            "B2": 0.4,
        }.get(level, 0.5)

    def score_activity(self, activity, A_points, T, K, prereq_map, mastery_map, now):
        if not A_points:
            return 0, {}

        # 1. coverage
        coverage = sum(T.get(p, 0) for p in A_points)

        # 2. density
        density = coverage / len(A_points)

        # 3. difficulty match
        learner_level = sum(K.get(p, 0) for p in A_points) / len(A_points)
        activity_level = self.difficulty_to_float(activity.metadata.general_difficulty)
        difficulty_score = 1 - abs(activity_level - learner_level)

        # 4. prerequisite penalty
        prereq_penalty = 0
        for p in A_points:
            for pre in prereq_map.get(p, []):
                if K.get(pre, 0) < 0.5:
                    prereq_penalty += 1

        # 5. learning gain
        gain = sum((1 - K.get(p, 0)) for p in A_points)

        # 6. recency penalty
        recency_penalty = 0
        for p in A_points:
            m = mastery_map.get(p)
            if m and m.last_attempt_at:
                delta = (now - m.last_attempt_at).total_seconds()
                recency_penalty += math.exp(-delta / 86400)

        score = (
            0.35 * coverage
            + 0.15 * density
            + 0.15 * difficulty_score
            + 0.20 * gain
            - 0.10 * prereq_penalty
            - 0.05 * recency_penalty
        )

        return score, {
            "coverage": coverage,
            "density": density,
            "difficulty": difficulty_score,
            "gain": gain,
            "prereq_penalty": prereq_penalty,
        }

    def explain(self, activity, A_points, T, K):
        reasons = []

        weak = [p for p in A_points if T.get(p, 0) >= 1.0]
        if weak:
            reasons.append(f"targets weak concepts: {weak[:3]}")

        reinforce = [p for p in A_points if 0.4 < T.get(p, 0) < 1.0]
        if reinforce:
            reasons.append(f"reinforces related concepts: {reinforce[:3]}")

        avg = sum(K.get(p, 0) for p in A_points) / len(A_points)
        reasons.append(f"fits your level (avg mastery ≈ {avg:.2f})")

        return reasons

    def recommend_activities(
        self,
        learner: Learner,
        atomic_points: List[AtomicPoint],
        activities: List[Activity],
        top_k: int = 5,
    ):
        now = datetime.utcnow()

        # 1. knowledge
        K = self.build_knowledge_state(learner, atomic_points)

        mastery_map = {str(m.atomic_point_id): m for m in learner.mastery_records}

        # 2. graph
        prereq_map, similar_map = self.build_graph(atomic_points)

        # 3. target set
        T = self.build_target_set(K, prereq_map, similar_map)

        results = []

        for activity in activities:
            A_points = self.extract_activity_points(activity)

            score, breakdown = self.score_activity(
                activity,
                A_points,
                T,
                K,
                prereq_map,
                mastery_map,
                now,
            )

            results.append(
                {
                    "activity_id": str(activity.id),
                    "title": activity.metadata.title,
                    "score": score,
                    "reasons": self.explain(activity, A_points, T, K),
                    "breakdown": breakdown,
                }
            )

        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:top_k]

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
