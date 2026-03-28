import re

_QUESTION_PATTERNS = [
    r"\?$",
    r"\b(can|could|would|will|do|does|did|is|are|was|were|have|has|had)\s+you\b",
    r"\b(what|how|why|when|where|who|which)\s+.{0,30}\s+you\b",  # question word must lead to "you"
    r"\b(tell (me|us)|walk (me|us) through|explain|describe|elaborate)\b",
    r"\b(thoughts|opinion|take|view|perspective)\s+on\b",
    r"\b(give us|give me)\b",
    r"\bany (thoughts|questions|concerns|objections|ideas|updates)\b",
    r"\bmake sense\b",
    r"\b(agree|disagree)\s+(with that|on that)?\b",
    r"\bright\?",
    r"\byeah\?",
    r"\bsound good\b",
    r"\byour\b",  # implicit address — "your thoughts", "your take", "what's your..."
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _QUESTION_PATTERNS]


def is_mentioned(text: str, name: str, team: str) -> bool:
    """
    Returns True if the user's name or team is mentioned anywhere in the text.
    """
    text_lower = text.lower()
    return name.lower() in text_lower or team.lower() in text_lower


def is_directed_at_me(text: str, name: str) -> bool:
    """
    Returns True if the text contains the user's name and matches
    at least one question pattern.
    """
    name_mentioned = name.lower() in text.lower()
    if not name_mentioned:
        return False
    return any(p.search(text) for p in _COMPILED)


def should_check_llm(text: str, name: str, team: str, project: str) -> bool:
    """
    Loose gate before the LLM classifier.
    Fires if any personal reference (name/team/project) is present
    OR if a question pattern is matched — either alone is sufficient.
    The LLM then decides whether it actually requires a response.
    """
    text_lower = text.lower()
    has_reference = (
        name.lower() in text_lower
        or (team and team.lower() in text_lower)
        or (project and project.lower() in text_lower)
    )
    has_question = any(p.search(text) for p in _COMPILED)
    return has_reference or has_question
