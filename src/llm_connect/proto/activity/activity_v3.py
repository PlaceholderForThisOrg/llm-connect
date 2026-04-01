activity_v3 = {
    "id": "ac_001",
    "type": "ROLE_PLAY",
    "metadata": {
        "title": "Restaurant Dining Experience",
        "location": "Italian restaurant",
        "npc_name": "Emma",
        "npc_role": "Waitress",
        "npc_personality": "Friendly, polite, slightly proactive",
        "context": "The learner enters a restaurant, has a reservation, orders food, and pays the bill.",
        "general_goal": "Successfully complete a full restaurant interaction using polite English.",
        "success_criteria": [
            "Learner completes ordering",
            "Learner asks for at least one item politely",
            "Learner handles bill interaction",
        ],
    },
    "general_difficulty": "B1",
    "estimated_time": "300",
    "interactions": {
        # ─────────────────────────────
        # 0. NPC greets
        # ─────────────────────────────
        "0": {
            "id": "0",
            "of": "SYSTEM",
            "description": "Waitress greets the customer",
            "goal": "Trigger learner to respond with reservation or request a table",
            "atomic_points": [],
            "nxt_poss_interactions": ["1"],
        },
        # ─────────────────────────────
        # 1. Learner mentions reservation
        # ─────────────────────────────
        "1": {
            "id": "1",
            "of": "LEARNER",
            "description": "Learner responds to greeting",
            "goal": "State they have a reservation",
            "atomic_points": ["ap_v_003", "ap_f_003"],
            "nxt_poss_interactions": ["2"],
        },
        # ─────────────────────────────
        # 2. NPC confirms and seats
        # ─────────────────────────────
        "2": {
            "id": "2",
            "of": "SYSTEM",
            "description": "Waitress confirms reservation and leads to table",
            "goal": "Transition to ordering phase",
            "atomic_points": [],
            "nxt_poss_interactions": ["3"],
        },
        # ─────────────────────────────
        # 3. Learner asks for menu
        # ─────────────────────────────
        "3": {
            "id": "3",
            "of": "LEARNER",
            "description": "Learner asks for menu",
            "goal": "Use polite request to ask for menu",
            "atomic_points": ["ap_f_002", "ap_v_001", "ap_g_001"],
            "nxt_poss_interactions": ["4"],
        },
        # ─────────────────────────────
        # 4. NPC gives menu + prompt
        # ─────────────────────────────
        "4": {
            "id": "4",
            "of": "SYSTEM",
            "description": "Waitress gives menu and asks for order or offers help",
            "goal": "Encourage learner to order or ask recommendation",
            "atomic_points": [],
            "nxt_poss_interactions": ["5", "6"],
        },
        # ─────────────────────────────
        # 5. Learner orders directly
        # ─────────────────────────────
        "5": {
            "id": "5",
            "of": "LEARNER",
            "description": "Learner orders food and/or drink",
            "goal": "Place an order using polite structure",
            "atomic_points": ["ap_f_001", "ap_g_001", "ap_v_005", "ap_v_007"],
            "nxt_poss_interactions": ["7"],
        },
        # ─────────────────────────────
        # 6. Learner asks recommendation
        # ─────────────────────────────
        "6": {
            "id": "6",
            "of": "LEARNER",
            "description": "Learner asks for recommendation",
            "goal": "Ask for suggestion using correct phrase",
            "atomic_points": ["ap_f_004", "ap_g_002"],
            "nxt_poss_interactions": ["8"],
        },
        # ─────────────────────────────
        # 7. NPC confirms order
        # ─────────────────────────────
        "7": {
            "id": "7",
            "of": "SYSTEM",
            "description": "Waitress confirms order",
            "goal": "Transition to dining phase",
            "atomic_points": [],
            "nxt_poss_interactions": ["9"],
        },
        # ─────────────────────────────
        # 8. NPC gives recommendation
        # ─────────────────────────────
        "8": {
            "id": "8",
            "of": "SYSTEM",
            "description": "Waitress recommends dish",
            "goal": "Guide learner to order after recommendation",
            "atomic_points": [],
            "nxt_poss_interactions": ["5"],
        },
        # ─────────────────────────────
        # 9. NPC checks after meal
        # ─────────────────────────────
        "9": {
            "id": "9",
            "of": "SYSTEM",
            "description": "Waitress asks if everything is okay",
            "goal": "Prompt learner to request bill",
            "atomic_points": [],
            "nxt_poss_interactions": ["10"],
        },
        # ─────────────────────────────
        # 10. Learner asks for bill
        # ─────────────────────────────
        "10": {
            "id": "10",
            "of": "LEARNER",
            "description": "Learner requests the bill",
            "goal": "Use polite structure to ask for bill",
            "atomic_points": ["ap_f_002", "ap_v_006"],
            "nxt_poss_interactions": ["11"],
        },
        # ─────────────────────────────
        # 11. NPC gives payment options
        # ─────────────────────────────
        "11": {
            "id": "11",
            "of": "SYSTEM",
            "description": "Waitress presents bill and asks payment method",
            "goal": "Trigger learner decision",
            "atomic_points": [],
            "nxt_poss_interactions": ["12"],
        },
        # ─────────────────────────────
        # 12. Learner chooses payment
        # ─────────────────────────────
        "12": {
            "id": "12",
            "of": "LEARNER",
            "description": "Learner chooses how to pay",
            "goal": "Respond naturally (card or cash)",
            "atomic_points": [],
            "nxt_poss_interactions": ["13"],
        },
        # ─────────────────────────────
        # 13. NPC completes payment
        # ─────────────────────────────
        "13": {
            "id": "13",
            "of": "SYSTEM",
            "description": "Waitress processes payment and thanks",
            "goal": "Prompt learner to close conversation",
            "atomic_points": [],
            "nxt_poss_interactions": ["14"],
        },
        # ─────────────────────────────
        # 14. Learner says goodbye
        # ─────────────────────────────
        "14": {
            "id": "14",
            "of": "LEARNER",
            "description": "Learner ends conversation",
            "goal": "Say thank you and goodbye",
            "atomic_points": [],
            "nxt_poss_interactions": [],
        },
    },
}
