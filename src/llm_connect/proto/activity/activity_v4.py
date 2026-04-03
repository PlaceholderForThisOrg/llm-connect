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
        # Greeting
        "0": {
            "goal": "Greet the waitress",
            "atomic_points": ["greeting_basic", "polite_expression"],
            "next_possibles": ["1"],
        },
        # Reservation
        "1": {
            "goal": "Mention having a reservation",
            "atomic_points": ["reservation_phrase", "name_expression"],
            "next_possibles": ["2"],
        },
        # Confirm reservation (NPC leads, learner responds)
        "2": {
            "goal": "Confirm reservation details (time / name)",
            "atomic_points": ["confirm_information", "short_answer"],
            "next_possibles": ["3"],
        },
        # Seating + menu intro
        "3": {
            "goal": "Respond politely when being seated",
            "atomic_points": ["gratitude_expression"],
            "next_possibles": ["4", "5"],
        },
        # Ask for recommendation (optional branch)
        "4": {
            "goal": "Ask for today's recommendation",
            "atomic_points": ["question_polite", "recommendation_phrase"],
            "next_possibles": ["5"],
        },
        # Order food
        "5": {
            "goal": "Order food and drinks",
            "atomic_points": ["ordering_food", "would_like"],
            "next_possibles": ["6"],
        },
        # Confirm order
        "6": {
            "goal": "Confirm or clarify the order",
            "atomic_points": ["confirmation_phrase", "correction_expression"],
            "next_possibles": ["7"],
        },
        # Food arrives
        "7": {
            "goal": "Respond when food is served",
            "atomic_points": ["gratitude_expression", "polite_reaction"],
            "next_possibles": ["8"],
        },
        # During meal (free interaction / filler)
        "8": {
            "goal": "Make a simple comment about the food",
            "atomic_points": ["opinion_expression", "food_adjective"],
            "next_possibles": ["9"],
        },
        # Ask for bill
        "9": {
            "goal": "Request the bill",
            "atomic_points": ["asking_bill", "polite_request"],
            "next_possibles": ["10"],
        },
        # Payment choice
        "10": {
            "goal": "Choose payment method (card or cash)",
            "atomic_points": ["payment_expression"],
            "next_possibles": ["11"],
        },
        # Payment handling
        "11": {
            "goal": "Respond during payment process",
            "atomic_points": ["short_response", "confirmation_phrase"],
            "next_possibles": ["12"],
        },
        # Thank you
        "12": {
            "goal": "Say thank you",
            "atomic_points": ["gratitude_expression"],
            "next_possibles": ["13"],
        },
        # Goodbye
        "13": {
            "goal": "Say goodbye and close the interaction",
            "atomic_points": ["goodbye_expression"],
            "next_possibles": [],
        },
    },
}
