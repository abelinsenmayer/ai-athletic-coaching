#!/usr/bin/env python3
"""
Criterion module for representing evaluation criteria for grading exercises.
"""

from enum import Enum
from dataclasses import dataclass
from pathlib import Path
from typing import List

from ..pose import Pose
from ..google.prompt_gemini import prompt_gemini


class Importance(Enum):
    """Enum representing the importance level of a criterion."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class EvalCriterion:
    """Represents a single evaluation criterion for an exercise."""
    name: str
    long_description: str
    importance: Importance

    def enhance_using_key_poses(self, key_poses: List[Pose]) -> None:
        """Use key poses for the parent Exercise to add additional specificity and context to this criterion."""
        if not key_poses:
            return
        
        # Read prompt template
        prompt_path = Path(__file__).parent / "prompts" / "enhance_criteria.txt"
        with open(prompt_path, 'r', encoding='utf-8') as f:
            template = f.read().strip()
        
        # Format key poses as string representations
        key_poses_str = "\n".join([str(pose) for pose in key_poses])
        
        # Construct prompt using template
        prompt = template.format(
            criterion_description=self.long_description,
            key_poses=key_poses_str
        )
        
        # Send to Gemini and get enhanced description
        try:
            enhanced_description = prompt_gemini(prompt).strip()
            if enhanced_description:
                self.long_description = enhanced_description
        except Exception as e:
            # If enhancement fails, keep original description
            print(f"Warning: Failed to enhance criterion '{self.name}': {e}")

