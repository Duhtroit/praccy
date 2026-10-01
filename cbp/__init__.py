"""Praccy -- local practice, five languages, strict output types."""

from .engine import evaluate, load_questions, all_tags
from .adapters import LANGUAGES
from .errors import RunError

__all__ = ["evaluate", "load_questions", "all_tags", "LANGUAGES", "RunError"]
