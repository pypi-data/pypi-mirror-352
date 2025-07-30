"""Common guardrails data class."""

from enum import Enum
from typing import List

from dataclasses import dataclass


class GuardrailAction(str, Enum):
    """Enum representing the action to be taken for guardrail rules."""

    BLOCK = "block"
    LOG = "log"


@dataclass(frozen=True)
class Guardrail:
    """Represents a single guardrail rule."""

    id: str
    name: str
    content: str
    action: GuardrailAction


@dataclass(frozen=True)
class GuardrailRuleSet:
    """Grouped guardrail rules separated by their action."""

    blocking_guardrails: List[Guardrail]
    logging_guardrails: List[Guardrail]
