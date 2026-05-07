from typing import Optional

from llm_connect.models.AtomicPoint import AtomicPoint


def format_examples(examples: Optional[str]) -> str:
    if not examples or not str(examples).strip():
        return "(none)"
    return str(examples).strip()


def build_semantic_text(ap: AtomicPoint) -> str:
    desc = ap.description if ap.description is not None else "(none)"
    return f"""
Type: {ap.type}
Name: {ap.name}
Level: {ap.level}

Description:
{desc}

Examples:
{format_examples(ap.examples)}
""".strip()
