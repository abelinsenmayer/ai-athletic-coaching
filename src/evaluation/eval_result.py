#!/usr/bin/env python3
"""
Evaluation result data class for video clip assessment.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict


class PerformanceLevel(Enum):
    """Enum representing performance level for a criterion."""
    POOR = 0.0
    ADEQUATE = 0.5
    EXCELLENT = 1.0


@dataclass
class CriterionScore:
    """Represents the score for a single evaluation criterion."""
    name: str
    performance: PerformanceLevel


@dataclass
class EvalResult:
    """Represents the result of evaluating a video clip."""
    criteria_scores: List[CriterionScore] = field(default_factory=list)
    
    @classmethod
    def from_llm_response(cls, response_text: str) -> 'EvalResult':
        """Parse LLM response text into EvalResult.
        
        Expected format:
        Each line: criterion_name,score (where score is 0.0, 0.5, or 1.0)
        
        Args:
            response_text: Raw text response from LLM
            
        Returns:
            EvalResult with parsed criteria scores
        """
        lines = response_text.strip().split('\n')
        if len(lines) == 0:
            raise ValueError("Response is empty")
        
        # Parse criterion scores
        criteria_scores = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            try:
                parts = line.split(',')
                if len(parts) != 2:
                    continue
                    
                name = parts[0].strip()
                numeric_score = float(parts[1].strip())
                
                # Convert numeric score to PerformanceLevel enum
                performance = None
                for level in PerformanceLevel:
                    if level.value == numeric_score:
                        performance = level
                        break
                
                if performance is None:
                    continue
                    
                criteria_scores.append(CriterionScore(name=name, performance=performance))
            except (ValueError, IndexError):
                continue
        
        return cls(criteria_scores=criteria_scores)
