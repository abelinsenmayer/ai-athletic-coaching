#!/usr/bin/env python3
"""
Grading module for comparing evaluation results.
"""

from dataclasses import dataclass
from decimal import Decimal
from .eval_result import EvalResult
from .ollama.ollama_prompt import ollama_prompt


@dataclass
class EvaluationGrade:
    """Data class containing grading results for evaluation comparisons."""
    feedbackAccuracy: Decimal
    scoreAccuracy: Decimal


def gradeEvaluation(expected: EvalResult, actual: EvalResult) -> EvaluationGrade:
    """
    Compare expected and actual evaluation results.
    
    Args:
        expected: The correct evaluation result from the eval file
        actual: The evaluation result returned by evaluateClip
    """
    print(f"Expected result: score={expected.score}, feedback='{expected.feedbackText}'")
    print(f"Actual result: score={actual.score}, feedback='{actual.feedbackText}'")
    
    # Use Ollama to grade the feedback comparison
    grading_prompt = f"""
    Please compare the following two pieces of feedback text and rate how well the actual feedback captures the key points of the expected feedback.

    Expected feedback: "{expected.feedbackText}"
    Actual feedback: "{actual.feedbackText}"

    Respond with only a single number between 0 and 10 (inclusive) where:
    - 0 = The actual feedback completely misses the key points
    - 5 = The actual feedback captures some key points but misses others
    - 10 = The actual feedback perfectly captures all key points

    Your response should be just the number, nothing else. You may include decimal values.
    """
    
    try:
        grade = ollama_prompt(grading_prompt)
    except Exception as e:
        print(f"Error comparing feedback text: {e}")
        grade = 0
    
    return EvaluationGrade(
        feedbackAccuracy=Decimal(grade),
        scoreAccuracy=Decimal(10 - abs(expected.score - actual.score))
    )
