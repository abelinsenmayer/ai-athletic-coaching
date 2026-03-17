#!/usr/bin/env python3
"""
Grading module for comparing evaluation results.
"""

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from .eval_result import EvalResult
from ..ollama.ollama_prompt import ollama_prompt


@dataclass
class EvaluationGrade:
    """Data class containing grading results for evaluation comparisons."""
    coachingAccuracy: Decimal
    feedbackRelevance: Decimal
    coachingTone: Decimal
    scoreAccuracy: Decimal
    assessmentText: str


def gradeEvaluation(expected: EvalResult, actual: EvalResult) -> EvaluationGrade:
    """
    Compare expected and actual evaluation results.
    
    Args:
        expected: The correct evaluation result from the eval file
        actual: The evaluation result returned by evaluateClip
    """
    print(f"Expected result: score={expected.score}, feedback='{expected.feedbackText}'")
    print(f"Actual result: score={actual.score}, feedback='{actual.feedbackText}'")
    
    # Load grading prompt from file
    prompt_path = Path(__file__).parent / "prompts" / "grading_prompt.txt"
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
    except Exception as e:
        print(f"Error loading grading prompt: {e}")
        # Fallback to default values
        return EvaluationGrade(
            coachingAccuracy=Decimal('0'),
            feedbackRelevance=Decimal('0'),
            coachingTone=Decimal('0'),
            scoreAccuracy=Decimal(10 - abs(expected.score - actual.score)),
            assessmentText=""
        )
    
    # Format the prompt with expected and actual feedback
    grading_prompt = prompt_template.format(
        expected_feedback=expected.feedbackText,
        actual_feedback=actual.feedbackText
    )
    
    try:
        grade_response = ollama_prompt(grading_prompt)
        # Parse the first line for the three scores: coaching_accuracy,feedback_relevance,coaching_tone
        lines = grade_response.strip().split('\n')
        if len(lines) >= 1:
            first_line = lines[0].strip()
            scores = first_line.split(',')
            if len(scores) == 3:
                coaching_accuracy = Decimal(scores[0].strip())
                feedback_relevance = Decimal(scores[1].strip())
                coaching_tone = Decimal(scores[2].strip())
            else:
                print(f"Unexpected score format on first line: {first_line}")
                coaching_accuracy = feedback_relevance = coaching_tone = Decimal('0')
            assessment_text = '\n'.join(lines[1:])
            print(f"Assessment text: {assessment_text}")
        else:
            print(f"Empty response from grader")
            coaching_accuracy = feedback_relevance = coaching_tone = Decimal('0')
    except Exception as e:
        print(f"Error comparing feedback text: {e}")
        coaching_accuracy = feedback_relevance = coaching_tone = Decimal('0')
    
    return EvaluationGrade(
        coachingAccuracy=coaching_accuracy,
        feedbackRelevance=feedback_relevance,
        coachingTone=coaching_tone,
        scoreAccuracy=Decimal(10 - abs(expected.score - actual.score)),
        assessmentText=assessment_text,
    )
