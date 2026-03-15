#!/usr/bin/env python3
"""
AI Athletic Coaching - Evaluation System Package
"""

from .eval_result import EvalResult
from .evaluate_clip import evaluateClip
from .grade_evaluations import gradeEvaluations

__all__ = ['EvalResult', 'evaluateClip', 'gradeEvaluations']
