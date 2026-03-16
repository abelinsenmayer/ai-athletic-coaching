#!/usr/bin/env python3
"""
Evaluation module for AI Athletic Coaching system.
"""

from .eval_result import EvalResult
from .evaluate_clip import evaluateClip
from .grade_evaluation import gradeEvaluation, EvaluationGrade

__all__ = ['EvalResult', 'evaluateClip', 'gradeEvaluation', 'EvaluationGrade']
