from datetime import date

today = str(date.today())

# ─────────────────────────────────────────────────────────────────
# ATOMIC POINTS
# Three types:
#   grammar  — underlying rules (ap_g_*)
#   vocabulary — individual words (ap_v_*)
#   fluency  — fixed phrases / chunks (ap_f_*)
#
# related[] links follow three patterns:
#   grammar  → fluency   : the rule is the foundation for the phrase
#   vocab    → fluency   : the word slots into the phrase
#   vocab    ↔ vocab     : sibling words taught together
# ─────────────────────────────────────────────────────────────────

atomic_points_v1 = [
    # ── Grammar ───────────────────────────────────────────────────
    {
        "id": "ap_g_001",
        "type": "grammar",
        "name": "Polite requests with 'could' and 'would'",
        "description": "Used to make polite requests in service situations.",
        "examples": ["Could I see the menu?", "Would you bring us some water?"],
        "level": "B1",
        "popularity": 0.95,
        "tags": ["restaurant", "politeness"],
        "related": ["ap_f_001", "ap_f_002"],
        "created_at": today,
        "updated_at": today,
        "evidence_of_grasp": [
            "used 'could I'",
            "used 'would you'",
            "used 'I'd like'",
            "used 'I would like'",
        ],
        "evidence_of_confusion": [
            "used 'I want' with no modal",
            "stated item with no request verb",
        ],
        "hints": [
            "Tip: in English, 'I want...' sounds a bit direct in a restaurant. "
            "Try starting with 'I'd like...' or 'Could I have...' instead.",
            "The two most natural patterns are: 'I'd like [item], please' "
            "and 'Could I have [item]?'",
            "Full example: 'Could I have the pasta, please?' "
            "or 'I'd like a glass of water.'",
        ],
    },
    {
        "id": "ap_g_002",
        "type": "grammar",
        "name": "Using 'some' and 'any' for requests",
        "description": "Used to talk about quantities in questions and requests.",
        "examples": ["Can I have some water?", "Do you have any vegetarian dishes?"],
        "level": "B1",
        "popularity": 0.9,
        "tags": ["food", "quantity"],
        "related": ["ap_v_002", "ap_v_007"],
        "created_at": today,
        "updated_at": today,
        "evidence_of_grasp": [
            "used 'some' in a positive request",
            "used 'any' in a question",
        ],
        "evidence_of_confusion": [
            "used 'any' in a positive request",
            "used 'some' in a question",
            "omitted determiner entirely",
        ],
        "hints": [
            "Tip: use 'some' when making a request ('Can I have some water?') "
            "and 'any' when asking a question ('Do you have any vegetarian options?').",
            "Rule: 'some' for offers and requests, 'any' for questions and negatives.",
            "Examples: 'Could I have some bread?' and 'Do you have any gluten-free options?'",
        ],
    },
    # ── Vocabulary ────────────────────────────────────────────────
    {
        "id": "ap_v_001",
        "type": "vocabulary",
        "name": "menu",
        "description": "A list of food and drinks available in a restaurant.",
        "examples": ["Could I see the menu?", "The menu looks great."],
        "level": "B1",
        "popularity": 0.95,
        "tags": ["restaurant"],
        "related": ["ap_f_002"],
        "created_at": today,
        "updated_at": today,
        "evidence_of_grasp": [
            "used 'menu' correctly",
            "asked for the menu by name",
        ],
        "evidence_of_confusion": [
            "pointed or gestured instead of using the word",
            "called it 'the card' or 'the book'",
        ],
        "hints": [
            "The list of dishes is called 'the menu'. "
            "You can ask: 'Could I see the menu, please?'",
            "Full phrase: 'Could I have the menu, please?' — "
            "this uses the same pattern as many other restaurant requests.",
        ],
    },
    {
        "id": "ap_v_002",
        "type": "vocabulary",
        "name": "vegetarian",
        "description": "A person who does not eat meat, or a dish without meat.",
        "examples": ["I'm vegetarian.", "Do you have any vegetarian dishes?"],
        "level": "B1",
        "popularity": 0.9,
        "tags": ["food", "diet"],
        "related": ["ap_g_002", "ap_f_004"],
        "created_at": today,
        "updated_at": today,
        "evidence_of_grasp": [
            "used 'vegetarian' correctly",
            "asked about vegetarian options using the word",
        ],
        "evidence_of_confusion": [
            "said 'I don't eat meat' without using the word 'vegetarian'",
            "confused 'vegan' and 'vegetarian'",
        ],
        "hints": [
            "The word is 'vegetarian' — it means no meat or fish. "
            "You can say: 'I'm vegetarian' or 'Do you have any vegetarian dishes?'",
            "Natural question: 'Do you have any vegetarian options?' — "
            "notice 'any' because it is a question.",
        ],
    },
    {
        "id": "ap_v_003",
        "type": "vocabulary",
        "name": "reservation",
        "description": "An arrangement to have a table saved at a restaurant.",
        "examples": ["I have a reservation.", "We made a reservation online."],
        "level": "B1",
        "popularity": 0.88,
        "tags": ["restaurant"],
        "related": ["ap_f_003"],
        "created_at": today,
        "updated_at": today,
        "evidence_of_grasp": [
            "used 'reservation' correctly",
            "said 'I have a reservation'",
            "said 'I booked a table'",
        ],
        "evidence_of_confusion": [
            "didn't know how to say they had booked",
            "said 'I have a booking' — acceptable but less natural",
        ],
        "hints": [
            "If you booked a table in advance, say: 'I have a reservation.'",
            "You can also say 'I booked a table' — both are correct. "
            "If you want to book on the spot: 'I'd like to make a reservation.'",
        ],
    },
    {
        "id": "ap_v_004",
        "type": "vocabulary",
        "name": "starter",
        "description": "A small dish served before the main course.",
        "examples": ["I'll have soup as a starter.", "What starters do you have?"],
        "level": "B1",
        "popularity": 0.82,
        "tags": ["meal"],
        "related": ["ap_v_005"],
        "created_at": today,
        "updated_at": today,
        "evidence_of_grasp": [
            "used 'starter' correctly",
            "used 'appetizer'",
            "asked 'What starters do you have?'",
        ],
        "evidence_of_confusion": [
            "called it 'the first dish' or 'the small plate'",
            "didn't know the word and described it instead",
        ],
        "hints": [
            "The small dish before the main meal is called a 'starter' "
            "(or 'appetizer' in American English).",
            "You can ask: 'What starters do you have?' "
            "or order with: 'I'd like the soup as a starter, please.'",
        ],
    },
    {
        "id": "ap_v_005",
        "type": "vocabulary",
        "name": "main course",
        "description": "The principal dish of a meal.",
        "examples": [
            "I'll have steak for the main course.",
            "The main course comes with rice.",
        ],
        "level": "B1",
        "popularity": 0.9,
        "tags": ["meal"],
        "related": ["ap_v_004", "ap_f_001"],
        "created_at": today,
        "updated_at": today,
        "evidence_of_grasp": [
            "used 'main course' correctly",
            "used 'main' as shorthand",
            "ordered using 'for my main'",
        ],
        "evidence_of_confusion": [
            "called it 'the big plate' or 'the second dish'",
            "didn't distinguish it from the starter",
        ],
        "hints": [
            "The main dish is called the 'main course', or just 'the main'.",
            "Natural ordering phrase: 'For my main course, I'd like the pasta, please.'",
        ],
    },
    {
        "id": "ap_v_006",
        "type": "vocabulary",
        "name": "bill",
        "description": "The total amount to pay for a meal.",
        "examples": ["Could we have the bill?", "The bill is $30."],
        "level": "B1",
        "popularity": 0.93,
        "tags": ["payment"],
        "related": ["ap_f_002"],
        "created_at": today,
        "updated_at": today,
        "evidence_of_grasp": [
            "used 'bill' correctly",
            "said 'Could I have the bill?'",
            "said 'check' (American English equivalent)",
        ],
        "evidence_of_confusion": [
            "said 'I want to pay' without using 'bill'",
            "didn't know how to ask and waited in silence",
        ],
        "hints": [
            "When you're ready to pay, ask: 'Could I have the bill, please?' "
            "This uses the same phrase as asking for the menu — just swap the word.",
            "'Bill' is British English; 'check' is American English — both are understood.",
        ],
    },
    {
        "id": "ap_v_007",
        "type": "vocabulary",
        "name": "water",
        "description": "A common drink served in restaurants.",
        "examples": ["Can I have some water?", "Still or sparkling water?"],
        "level": "B1",
        "popularity": 0.98,
        "tags": ["drink"],
        "related": ["ap_g_002", "ap_f_001"],
        "created_at": today,
        "updated_at": today,
        "evidence_of_grasp": [
            "asked for water using a complete request",
            "used 'some water' correctly",
            "specified still or sparkling",
        ],
        "evidence_of_confusion": [
            "just said 'water' with no request form",
            "didn't know how to specify still vs sparkling",
        ],
        "hints": [
            "To ask for water: 'Could I have some water, please?' "
            "or 'I'd like some water.'",
            "The waiter may ask 'Still or sparkling?' — "
            "'still' means flat water, 'sparkling' means fizzy.",
        ],
    },
    # ── Fluency ───────────────────────────────────────────────────
    {
        "id": "ap_f_001",
        "type": "fluency",
        "name": "I'd like...",
        "description": "A polite fixed phrase for ordering food or making requests.",
        "examples": ["I'd like a burger.", "I'd like some water."],
        "level": "B1",
        "popularity": 0.97,
        "tags": ["speaking", "ordering"],
        "related": ["ap_g_001", "ap_v_005", "ap_v_007"],
        "created_at": today,
        "updated_at": today,
        "evidence_of_grasp": [
            "used 'I'd like' to order",
            "used 'I would like' in full form",
        ],
        "evidence_of_confusion": [
            "used 'I want' instead",
            "used bare infinitive with no modal",
        ],
        "hints": [
            "'I'd like' is the contracted form of 'I would like' — "
            "very natural and polite for ordering.",
            "Pattern: 'I'd like [item], please.' — "
            "for example: 'I'd like the pasta, please.'",
        ],
    },
    {
        "id": "ap_f_002",
        "type": "fluency",
        "name": "Could I have...?",
        "description": "A polite fixed phrase for requesting items.",
        "examples": ["Could I have the menu?", "Could I have the bill?"],
        "level": "B1",
        "popularity": 0.96,
        "tags": ["politeness", "requesting"],
        "related": ["ap_g_001", "ap_v_001", "ap_v_006"],
        "created_at": today,
        "updated_at": today,
        "evidence_of_grasp": [
            "used 'Could I have...' correctly",
            "applied the frame to a new vocabulary item",
        ],
        "evidence_of_confusion": [
            "used 'Can I have' (acceptable but less formal)",
            "dropped 'could' and just named the item",
        ],
        "hints": [
            "'Could I have...' is one of the most useful phrases in a restaurant. "
            "You can use it for the menu, your food, the bill — anything.",
            "Pattern: 'Could I have [item], please?' — "
            "try it now: 'Could I have the menu, please?'",
        ],
    },
    {
        "id": "ap_f_003",
        "type": "fluency",
        "name": "make a reservation",
        "description": "Fixed verb phrase for booking a table.",
        "examples": ["I'd like to make a reservation.", "We made a reservation."],
        "level": "B1",
        "popularity": 0.88,
        "tags": ["restaurant", "booking"],
        "related": ["ap_v_003"],
        "created_at": today,
        "updated_at": today,
        "evidence_of_grasp": [
            "used 'make a reservation'",
            "said 'I have a reservation'",
        ],
        "evidence_of_confusion": [
            "said 'I booked' without 'reservation'",
            "didn't know the phrase",
        ],
        "hints": [
            "To book a table: 'I'd like to make a reservation.' "
            "To confirm you already booked: 'I have a reservation.'",
        ],
    },
    {
        "id": "ap_f_004",
        "type": "fluency",
        "name": "Do you have any recommendations?",
        "description": "Fixed phrase for asking staff for suggestions.",
        "examples": ["Do you have any recommendations?", "What do you recommend?"],
        "level": "B1",
        "popularity": 0.9,
        "tags": ["interaction", "asking"],
        "related": ["ap_g_002", "ap_v_002"],
        "created_at": today,
        "updated_at": today,
        "evidence_of_grasp": [
            "used 'recommendations' correctly",
            "asked 'What do you recommend?'",
            "asked for a suggestion naturally",
        ],
        "evidence_of_confusion": [
            "said 'What is good?' — too informal",
            "didn't know how to ask for a suggestion",
        ],
        "hints": [
            "To ask the waiter what's good: 'Do you have any recommendations?' "
            "or simply 'What do you recommend?'",
            "After mentioning a dietary need, this pairs naturally: "
            "'I'm vegetarian — do you have any recommendations?'",
        ],
    },
    {
        "id": "ap_g_101",
        "type": "grammar",
        "name": "Using 'I'd like to' for requests and intentions",
        "description": "Used to politely state what you want to do in a store.",
        "examples": [
            "I'd like to return this item.",
            "I'd like to exchange this, please.",
        ],
        "level": "B1",
        "popularity": 0.95,
        "tags": ["shopping", "politeness"],
        "related": ["ap_f_101", "ap_f_102"],
        "created_at": today,
        "updated_at": today,
        "evidence_of_grasp": [
            "used 'I'd like to return'",
            "used 'I'd like to exchange'",
        ],
        "evidence_of_confusion": [
            "used 'I want to return' directly",
            "stated 'return this' without a subject",
        ],
        "hints": [
            "In stores, 'I'd like to...' sounds more polite than 'I want to...'.",
            "Pattern: 'I'd like to + verb' → 'I'd like to return this item.'",
        ],
    },
    {
        "id": "ap_g_102",
        "type": "grammar",
        "name": "Present perfect for problems ('has broken')",
        "description": "Used to describe a problem that happened recently and is still relevant.",
        "examples": ["This has broken.", "The screen has stopped working."],
        "level": "B1",
        "popularity": 0.88,
        "tags": ["problems", "products"],
        "related": ["ap_f_103"],
        "created_at": today,
        "updated_at": today,
        "evidence_of_grasp": [
            "used 'has broken'",
            "used 'has stopped working'",
        ],
        "evidence_of_confusion": [
            "used 'is break'",
            "used only present tense 'it doesn't work' without context",
        ],
        "hints": [
            "Use 'has + past participle' for recent problems.",
            "Example: 'It has stopped working' sounds more natural than 'It stopped working' in this context.",
        ],
    },
    # ── Vocabulary ────────────────────────────────────────────────
    {
        "id": "ap_v_101",
        "type": "vocabulary",
        "name": "receipt",
        "description": "A paper or digital proof of purchase.",
        "examples": ["Here is my receipt.", "Do I need the receipt to return this?"],
        "level": "B1",
        "popularity": 0.95,
        "tags": ["shopping"],
        "related": ["ap_f_104"],
        "created_at": today,
        "updated_at": today,
        "evidence_of_grasp": [
            "used 'receipt' correctly",
            "offered the receipt when returning",
        ],
        "evidence_of_confusion": [
            "called it 'paper' or 'ticket'",
            "didn't know the word",
        ],
        "hints": [
            "The proof of purchase is called a 'receipt'.",
            "You can say: 'Here is my receipt.'",
        ],
    },
    {
        "id": "ap_v_102",
        "type": "vocabulary",
        "name": "refund",
        "description": "Money returned after returning a product.",
        "examples": ["I'd like a refund.", "Can I get a refund for this?"],
        "level": "B1",
        "popularity": 0.92,
        "tags": ["payment"],
        "related": ["ap_f_102"],
        "created_at": today,
        "updated_at": today,
        "evidence_of_grasp": [
            "used 'refund' correctly",
            "asked for a refund",
        ],
        "evidence_of_confusion": [
            "said 'give me money back'",
            "confused with 'discount'",
        ],
        "hints": [
            "'Refund' means you get your money back.",
            "Natural phrase: 'I'd like a refund, please.'",
        ],
    },
    {
        "id": "ap_v_103",
        "type": "vocabulary",
        "name": "exchange",
        "description": "To replace a product with another one.",
        "examples": [
            "I'd like to exchange this.",
            "Can I exchange it for another one?",
        ],
        "level": "B1",
        "popularity": 0.9,
        "tags": ["shopping"],
        "related": ["ap_f_101"],
        "created_at": today,
        "updated_at": today,
        "evidence_of_grasp": [
            "used 'exchange' correctly",
        ],
        "evidence_of_confusion": [
            "said 'change it' incorrectly",
        ],
        "hints": [
            "'Exchange' means to swap for another item.",
            "Example: 'I'd like to exchange this for a new one.'",
        ],
    },
    {
        "id": "ap_v_104",
        "type": "vocabulary",
        "name": "broken",
        "description": "Not working or damaged.",
        "examples": ["This is broken.", "The product arrived broken."],
        "level": "A2",
        "popularity": 0.98,
        "tags": ["problems"],
        "related": ["ap_f_103"],
        "created_at": today,
        "updated_at": today,
        "evidence_of_grasp": [
            "used 'broken' correctly",
        ],
        "evidence_of_confusion": [
            "said 'it break'",
            "used 'bad' instead of 'broken'",
        ],
        "hints": [
            "Use 'broken' to describe something not working.",
            "Example: 'This is broken.'",
        ],
    },
    # ── Fluency ───────────────────────────────────────────────────
    {
        "id": "ap_f_101",
        "type": "fluency",
        "name": "I'd like to return this",
        "description": "Fixed phrase for starting a return.",
        "examples": [
            "I'd like to return this item.",
        ],
        "level": "B1",
        "popularity": 0.97,
        "tags": ["shopping", "speaking"],
        "related": ["ap_g_101", "ap_v_103"],
        "created_at": today,
        "updated_at": today,
        "evidence_of_grasp": [
            "used full phrase naturally",
        ],
        "evidence_of_confusion": [
            "just said 'return this'",
        ],
        "hints": [
            "This is the most natural way to start a return.",
            "Pattern: 'I'd like to return this (item), please.'",
        ],
    },
    {
        "id": "ap_f_102",
        "type": "fluency",
        "name": "I'd like a refund",
        "description": "Fixed phrase for asking for money back.",
        "examples": [
            "I'd like a refund, please.",
        ],
        "level": "B1",
        "popularity": 0.95,
        "tags": ["payment"],
        "related": ["ap_v_102"],
        "created_at": today,
        "updated_at": today,
        "evidence_of_grasp": [
            "asked for a refund clearly",
        ],
        "evidence_of_confusion": [
            "used indirect unclear phrasing",
        ],
        "hints": [
            "Simple and direct: 'I'd like a refund, please.'",
        ],
    },
    {
        "id": "ap_f_103",
        "type": "fluency",
        "name": "It doesn't work / It's broken",
        "description": "Fixed phrases to explain the problem.",
        "examples": ["It doesn't work.", "It's broken."],
        "level": "A2",
        "popularity": 0.98,
        "tags": ["problems"],
        "related": ["ap_g_102", "ap_v_104"],
        "created_at": today,
        "updated_at": today,
        "evidence_of_grasp": [
            "explained problem clearly",
        ],
        "evidence_of_confusion": [
            "couldn't explain the issue",
        ],
        "hints": [
            "Use simple explanation: 'It doesn't work.'",
            "Or slightly stronger: 'It's broken.'",
        ],
    },
    {
        "id": "ap_f_104",
        "type": "fluency",
        "name": "Here is my receipt",
        "description": "Phrase for providing proof of purchase.",
        "examples": [
            "Here is my receipt.",
        ],
        "level": "B1",
        "popularity": 0.9,
        "tags": ["shopping"],
        "related": ["ap_v_101"],
        "created_at": today,
        "updated_at": today,
        "evidence_of_grasp": [
            "offered receipt naturally",
        ],
        "evidence_of_confusion": [
            "didn't know how to present receipt",
        ],
        "hints": [
            "When staff asks, say: 'Here is my receipt.'",
        ],
    },
]

# ── Runtime lookup ─────────────────────────────────────────────
ATOMIC_REGISTRY = {ap["id"]: ap for ap in atomic_points_v1}


# __ For prompt
def ap2str(d):
    return (
        f"""
[Knowledge]

Name: {d['name']}
Level: {d['level']}
Type: {d['type']}
Domain: {', '.join(d['tags'])}

Description:
{d['description']}

Examples:
- """
        + "\n- ".join(d["examples"])
        + f"""

Hints:
- """
        + "\n- ".join(d["hints"])
        + f"""

Evidence of Understanding:
- """
        + "\n- ".join(d["evidence_of_grasp"])
        + f"""

Common Mistakes:
- """
        + "\n- ".join(d["evidence_of_confusion"])
        + f"""

Metadata:
- ID: {d['id']}
- Related: {', '.join(d['related'])}
- Popularity: {d['popularity']}
- Created At: {d['created_at']}
- Updated At: {d['updated_at']}
""".strip()
    )
