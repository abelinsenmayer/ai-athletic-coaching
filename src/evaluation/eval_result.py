#!/usr/bin/env python3
"""
Evaluation result data class for video clip assessment.
"""

from dataclasses import dataclass


@dataclass
class EvalResult:
    """Represents the result of evaluating a video clip."""
    score: float
    feedbackText: str
