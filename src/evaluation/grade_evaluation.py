#!/usr/bin/env python3
"""
Grading module for comparing evaluation results.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict
from .eval_result import EvalResult, CriterionScore, PerformanceLevel
from ..ollama.ollama_prompt import ollama_prompt


@dataclass
class EvaluationGrade:
    """Data class containing grading results for evaluation comparisons."""
    criterion_scores: Dict[str, float]
    criterion_off_by: Dict[str, float]
    
    def get_accuracy_percentage(self) -> float:
        """Calculate overall accuracy as percentage."""
        if not self.criterion_scores:
            return 0.0
        
        total_score = sum(self.criterion_scores.values())
        return total_score / len(self.criterion_scores)


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
    criterion_off_by = {}
    
    for actual_criterion in actual.criteria_scores:
        criterion_name = actual_criterion.name
        
        if criterion_name in expected_criteria:
            expected_performance = expected_criteria[criterion_name]
            actual_performance = actual_criterion.performance
            
            # Score is 1.0 - absolute difference in expected and actual ratings
            accuracy_score = 1 - abs(expected_performance.value - actual_performance.value)
            criterion_scores[criterion_name] = accuracy_score
            
            # Calculate off_by value (actual - expected)
            off_by = actual_performance.value - expected_performance.value
            criterion_off_by[criterion_name] = off_by
        else:
            # If criterion not found in expected, mark as incorrect
            criterion_scores[criterion_name] = 0.0
            criterion_off_by[criterion_name] = 0.0
    
    # Check for expected criteria that weren't evaluated in actual
    for expected_criterion in expected.criteria_scores:
        if expected_criterion.name not in criterion_scores:
            criterion_scores[expected_criterion.name] = 0.0
            criterion_off_by[expected_criterion.name] = 0.0
    
    return EvaluationGrade(criterion_scores=criterion_scores, criterion_off_by=criterion_off_by)
    