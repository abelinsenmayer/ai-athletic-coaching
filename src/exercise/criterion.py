#!/usr/bin/env python3
"""
Criterion module for representing evaluation criteria for grading exercises.
"""

from enum import Enum
from dataclasses import dataclass


class Importance(Enum):
    """Enum representing the importance level of a criterion."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class EvalCriterion:
    """Represents a single evaluation criterion for an exercise."""
    name: str
    long_description: str
    importance: Importance
