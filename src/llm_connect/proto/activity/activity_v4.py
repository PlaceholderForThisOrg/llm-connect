activity_v4 = {
    "id": "ac_001",
    "type": "ROLE_PLAY",
    "title": "Restaurant Dining Experience",
    "metadata": {
        "location": "Italian restaurant",
        "npc_name": "Emma",
        "npc_role": "Waitress",
        "npc_personality": "Friendly, polite, slightly proactive",
        "additional_information": """
            - Menu includes pasta, pizza, salads, wine, desserts
            - Today's special: Seafood pasta
        """,
        "general_goal": "Successfully complete a full restaurant interaction using polite English.",
    },
    "general_difficulty": "B1",
    "estimated_time": "300",
    # Entry point
    "start_goals": ["0"],
    "goals": {
        "0": {
            "goal": "Greet the waitress",
            "atomic_points": ["ap_f_001"],  # I'd like / polite tone starter
            "next_possibles": ["1"],
        },
        "1": {
            "goal": "Mention having a reservation",
            "atomic_points": ["ap_v_003", "ap_f_003"],
            "next_possibles": ["2"],
        },
        "2": {
            "goal": "Confirm reservation details (time / name)",
            "atomic_points": ["ap_v_003"],
            "next_possibles": ["3"],
        },
        "3": {
            "goal": "Respond politely when being seated",
            "atomic_points": ["ap_g_001"],  # polite responses like "thank you"
            "next_possibles": ["4", "5"],
        },
        "4": {
            "goal": "Ask for today's recommendation",
            "atomic_points": ["ap_f_004", "ap_g_002", "ap_v_002"],
            "next_possibles": ["5"],
        },
        "5": {
            "goal": "Order food and drinks",
            "atomic_points": ["ap_f_001", "ap_g_001", "ap_v_005", "ap_v_007"],
            "next_possibles": ["6"],
        },
        "6": {
            "goal": "Confirm or clarify the order",
            "atomic_points": ["ap_f_001", "ap_g_001"],
            "next_possibles": ["7"],
        },
        "7": {
            "goal": "Respond when food is served",
            "atomic_points": ["ap_g_001"],
            "next_possibles": ["8"],
        },
        "8": {
            "goal": "Make a simple comment about the food",
            "atomic_points": ["ap_f_001"],
            "next_possibles": ["9"],
        },
        "9": {
            "goal": "Request the bill",
            "atomic_points": ["ap_f_002", "ap_v_006", "ap_g_001"],
            "next_possibles": ["10"],
        },
        "10": {
            "goal": "Choose payment method (card or cash)",
            "atomic_points": ["ap_g_001"],
            "next_possibles": ["11"],
        },
        "11": {
            "goal": "Respond during payment process",
            "atomic_points": ["ap_g_001"],
            "next_possibles": ["12"],
        },
        "12": {
            "goal": "Say thank you",
            "atomic_points": ["ap_g_001"],
            "next_possibles": ["13"],
        },
        "13": {
            "goal": "Say goodbye and close the interaction",
            "atomic_points": ["ap_g_001"],
            "next_possibles": [],
        },
    },
}
