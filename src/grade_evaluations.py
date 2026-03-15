#!/usr/bin/env python3
"""
Grading module for comparing evaluation results.
"""

from .eval_result import EvalResult


def gradeEvaluations(expected: EvalResult, actual: EvalResult) -> None:
    """
    Compare expected and actual evaluation results.
    
    Args:
        expected: The correct evaluation result from the eval file
        actual: The evaluation result returned by evaluateClip
    """
    print(f"Expected result: score={expected.score}, feedback='{expected.feedbackText}'")
    print(f"Actual result: score={actual.score}, feedback='{actual.feedbackText}'")
    
    # TODO: Implement grading logic
