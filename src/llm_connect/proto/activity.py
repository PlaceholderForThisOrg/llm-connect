activity_v1 = {
    "id": "activity_001",
    "type": "ROLE-PLAY",
    "description": "At the restaurant, learner wants to order food with the waiter",
    "context": "The waiter's name is ..., the restaurant name is ..., it is 7:00 p.m, and you're very hungry, ...",
    "goal": "You have to order your dinner successfully",
    "difficulty": "B1",
}


# ─────────────────────────────────────────────────────────────────
# ACTIVITY
# ─────────────────────────────────────────────────────────────────
#
# Atomic point assignment per checkpoint:
#
#   CP0  Greeting    → ap_v_003, ap_f_003
#   CP1  Menu req.   → ap_g_001, ap_v_001, ap_f_002
#   CP2  Menu Qs     → ap_g_002, ap_v_002, ap_v_004, ap_f_004
#   CP3  Ordering    → ap_g_001, ap_g_002, ap_v_005, ap_v_007, ap_f_001
#   CP4  Paying      → ap_g_001, ap_v_006, ap_f_002
#   CP5  Farewell    → []
#
# ap_g_001 spans CP1→CP3→CP4: introduced, practiced, assessed
# ap_f_002 spans CP1→CP4: same phrase frame, different vocab slot
# ap_v_004 introduced CP2, produced CP3: introduce then produce
# ─────────────────────────────────────────────────────────────────

activity_v2 = {
    "id": "activity_002",
    "type": "ROLE-PLAY",
    "description": "At the restaurant, the learner orders dinner from a waiter",
    "context": (
        "The waiter's name is Marco. The restaurant is La Piazza, a cozy Italian "
        "restaurant in the city centre. It is 7:00 p.m. on a Friday evening. "
        "The restaurant is moderately busy. The learner is dining alone and is hungry."
    ),
    "goal": "Order your dinner successfully — from being seated to paying the bill.",
    "difficulty": "B1",
    "checkpoint_num": 6,
    "checkpoints": {
        "0": {
            "name": "Greeting and seating",
            "scene_context": (
                "Marco sees the learner walk in. The restaurant has window seats, "
                "bar-side seats, and a quiet corner table available. "
                "The learner may or may not have a reservation."
            ),
            "learner_goal": (
                "Respond to Marco's greeting, mention a reservation if they have one, "
                "and choose where to sit"
            ),
            "npc_pressure": [
                "Greet warmly and ask how many are dining tonight",
                "Ask if they have a reservation",
                "Offer a genuine choice between two seating options",
                "Do not move to the menu until the learner has chosen a seat",
            ],
            "atomic_points": ["ap_v_003", "ap_f_003"],
            "ends_when": (
                "The learner has responded to the greeting and chosen where to sit"
            ),
            "next": "1",
        },
        "1": {
            "name": "Asking for the menu",
            "scene_context": (
                "The learner is now seated. Marco is standing nearby but has not "
                "handed over the menu yet. The learner needs to ask for it."
            ),
            "learner_goal": "Ask Marco for the menu using a polite request form",
            "npc_pressure": [
                "Wait for the learner to ask — do not hand over the menu automatically",
                "If the learner just points or says 'menu' with no request form, "
                "respond naturally but look slightly expectant",
                "Once asked correctly, hand it over warmly",
            ],
            "atomic_points": ["ap_g_001", "ap_v_001", "ap_f_002"],
            "ends_when": (
                "The learner has asked for the menu and Marco has handed it over"
            ),
            "next": "2",
        },
        "2": {
            "name": "Menu questions",
            "scene_context": (
                "Marco has given the learner the menu. Tonight's specials are a "
                "seafood risotto and a braised lamb shank. The learner may want to "
                "ask about vegetarian options or get a recommendation."
            ),
            "learner_goal": "Ask at least one question about the menu before ordering",
            "npc_pressure": [
                "Say 'Take your time' and give the learner a moment",
                "Mention the specials and describe them briefly",
                "If the learner goes quiet, gently ask 'Do you have any questions about the menu?'",
                "Answer questions warmly — this is the learner's research moment",
                "Do not take the order until the learner signals readiness",
            ],
            "atomic_points": ["ap_g_002", "ap_v_002", "ap_v_004", "ap_f_004"],
            "ends_when": (
                "The learner has asked at least one question and signals they are ready to order"
            ),
            "next": "3",
        },
        "3": {
            "name": "Placing the order",
            "scene_context": (
                "The learner is ready to order. Marco takes out his notepad. "
                "The menu has starters, mains, and drinks. "
                "The pasta is a popular main. The steak can be cooked to preference."
            ),
            "learner_goal": "Order at least a main course and a drink",
            "npc_pressure": [
                "Open with 'Are you ready to order?'",
                "After the learner orders their main, ask one natural follow-up question",
                "Ask about drinks separately after food",
                "Confirm the full order back before closing",
            ],
            "atomic_points": [
                "ap_g_001",
                "ap_g_002",
                "ap_v_005",
                "ap_v_007",
                "ap_f_001",
            ],
            "ends_when": (
                "The learner has ordered a main dish and a drink, "
                "and Marco has confirmed the full order"
            ),
            "next": "4",
        },
        "4": {
            "name": "Paying the bill",
            "scene_context": (
                "The learner has finished eating. Marco has not brought the bill. "
                "The learner needs to ask for it. "
                "Note: this mirrors CP1 — the same phrase frame 'Could I have...?' "
                "now applied to 'the bill' instead of 'the menu'."
            ),
            "learner_goal": "Ask for the bill politely",
            "npc_pressure": [
                "Do not bring the bill — wait for the learner to ask",
                "If the learner is quiet, softly ask 'Can I get you anything else?'",
                "Once asked, bring it and ask 'Cash or card?'",
            ],
            "atomic_points": ["ap_g_001", "ap_v_006", "ap_f_002"],
            "ends_when": (
                "The learner has asked for the bill and the payment exchange is complete"
            ),
            "next": "5",
        },
        "5": {
            "name": "Farewell",
            "scene_context": "The learner is leaving. Marco is near the door.",
            "learner_goal": "Say goodbye naturally",
            "npc_pressure": [
                "Thank the learner warmly",
                "Wish them a good evening and invite them to return",
            ],
            "atomic_points": [],
            "ends_when": "The learner has said goodbye in any natural form",
            "next": None,
        },
    },
}

test_activity = {
    "id": "activity_002",
    "type": "READING_AND_FINDING_INFORMATION",
    "description": "You received a advertisement from a dance club, where it offers a free class, but there are conditions to meet to join that class",
    "context": "You live in a small city, you actually have a lot of freetime at night, and you received that advertisement by chance, then you have to understand that advertisement to actually join the free dance class",
    "goal": "Understand the conditions and decide whether you can or can't join the club",
    "difficulty": "B2",
    "checkpoints": [],
}
