#!/usr/bin/env python3
"""
Exercise module for representing athletic exercises and their evaluation criteria.
"""

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List

from .criterion import EvalCriterion, Importance
from ..pose import Pose
from ..pose.generate_key_poses import generate_key_poses


@dataclass
class Exercise:
    """Represents an athletic exercise with its evaluation criteria."""
    name: str
    criteria: List[EvalCriterion] = field(default_factory=list)
    key_poses: List[Pose] = field(default_factory=list)
    
    def add_criterion(self, criterion: EvalCriterion) -> None:
        """Add a criterion to this exercise."""
        self.criteria.append(criterion)
    
    def get_criteria_by_importance(self, importance):
        """Get all criteria with the specified importance level."""
        return [c for c in self.criteria if c.importance == importance]

    
    def enhance_criteria_using_key_poses(self) -> None:
        """Enhance criteria using key poses."""
        for criterion in self.criteria:
            criterion.enhance_using_key_poses(self.key_poses)
    
    @classmethod
    def create_from_sources(cls, criteria_json_path: str | Path, template_video_path: str | Path) -> 'Exercise':
        """Create an Exercise from external sources.
        
        Args:
            criteria_json_path: Path to the JSON file containing exercise definition
            template_video_path: Path to the template video for this exercise
            
        Returns:
            Exercise: The parsed exercise object
        """
        # Load criteria from JSON file
        with open(criteria_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        criteria = []
        for criterion_data in data.get('criteria', []):
            criterion = EvalCriterion(
                name=criterion_data['name'],
                long_description=criterion_data['long_description'],
                importance=Importance(criterion_data['importance'])
            )
            criteria.append(criterion)
        
        # Load key poses from template video
        key_poses = generate_key_poses(template_video_path)

        for criterion in criteria:
            criterion.enhance_using_key_poses(key_poses)
        
        return cls(
            name=data['name'],
            criteria=criteria,
            key_poses=key_poses,
        )
    
    def __str__(self) -> str:
        """String representation of the exercise."""
        return f"Exercise(name='{self.name}', criteria_count={len(self.criteria)})"
