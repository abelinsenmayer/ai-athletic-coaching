#!/usr/bin/env python3
"""
Exercise module for representing athletic exercises and their evaluation criteria.
"""

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List

from .criterion import EvalCriterion, Importance


@dataclass
class Exercise:
    """Represents an athletic exercise with its evaluation criteria."""
    name: str
    criteria: List[EvalCriterion] = field(default_factory=list)
    
    def add_criterion(self, criterion: EvalCriterion) -> None:
        """Add a criterion to this exercise."""
        self.criteria.append(criterion)
    
    def get_criteria_by_importance(self, importance):
        """Get all criteria with the specified importance level."""
        return [c for c in self.criteria if c.importance == importance]
    
    @classmethod
    def from_json(cls, json_path: str | Path) -> 'Exercise':
        """Create an Exercise from a JSON file.
        
        Args:
            json_path: Path to the JSON file containing exercise definition
            
        Returns:
            Exercise: The parsed exercise object
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        criteria = []
        for criterion_data in data.get('criteria', []):
            criterion = EvalCriterion(
                name=criterion_data['name'],
                long_description=criterion_data['long_description'],
                importance=Importance(criterion_data['importance'])
            )
            criteria.append(criterion)
        
        return cls(
            name=data['name'],
            criteria=criteria
        )
    
    def __str__(self) -> str:
        """String representation of the exercise."""
        return f"Exercise(name='{self.name}', criteria_count={len(self.criteria)})"
