#!/usr/bin/env python3
"""
Grading module for comparing evaluation results.
"""

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Dict
from .eval_result import EvalResult, CriterionScore, PerformanceLevel
from ..ollama.ollama_prompt import ollama_prompt


@dataclass
class EvaluationGrade:
    """Data class containing grading results for evaluation comparisons."""
    criterion_scores: Dict[str, Decimal]
    
    def get_accuracy_percentage(self) -> Decimal:
        """Calculate overall accuracy as percentage."""
        if not self.criterion_scores:
            return Decimal('0')
        
        total_score = sum(self.criterion_scores.values())
        return total_score / Decimal(len(self.criterion_scores))


def gradeEvaluation(expected: EvalResult, actual: EvalResult) -> EvaluationGrade:
    """
    Compare expected and actual evaluation results based on criterion scores.
    
    Args:
        expected: The correct evaluation result from the eval file
        actual: The evaluation result returned by evaluateClip
        
    Returns:
        EvaluationGrade with criterion-by-criterion accuracy scores
    """
    # Create lookup for expected criteria
    expected_criteria = {c.name: c.performance for c in expected.criteria_scores}
    
    # Compare each actual criterion against expected
    criterion_scores = {}
    
    for actual_criterion in actual.criteria_scores:
        criterion_name = actual_criterion.name
        
        if criterion_name in expected_criteria:
            expected_performance = expected_criteria[criterion_name]
            actual_performance = actual_criterion.performance
            
            # Score is 1.0 if match, 0.0 if mismatch
            accuracy_score = Decimal('1.0') if expected_performance == actual_performance else Decimal('0.0')
            criterion_scores[criterion_name] = accuracy_score
        else:
            # If criterion not found in expected, mark as incorrect
            criterion_scores[criterion_name] = Decimal('0.0')
    
    # Check for expected criteria that weren't evaluated in actual
    for expected_criterion in expected.criteria_scores:
        if expected_criterion.name not in criterion_scores:
            criterion_scores[expected_criterion.name] = Decimal('0.0')
    
    return EvaluationGrade(criterion_scores=criterion_scores)
    