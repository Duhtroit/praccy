"""User-facing error types."""

from __future__ import annotations


class RunError(Exception):
    """A user's submitted code failed to run at all.

    Distinct from a *wrong answer*: a RunError means compile error, crash,
    or timeout, and the forensics view renders it differently.
    """

    def __init__(self, kind: str, message: str, language: str = ""):
        super().__init__(message)
        self.kind = kind  # "compile" | "runtime" | "timeout" | "interface"
        self.message = message
        self.language = language

    def __str__(self) -> str:
        return f"[{self.kind}] {self.message}"
