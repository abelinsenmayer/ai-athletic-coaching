#!/usr/bin/env python3
"""
Test case classes for video clip evaluation system with multiple trials support.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path

from src.evaluation.eval_result import EvalResult
from src.exercise.exercise import Exercise


@dataclass
class EvalTrial:
    """Represents a single evaluation trial for a video clip."""
    clip_name: str
    execise: Exercise
    expected_result: EvalResult
    actual_results: List[EvalResult] = field(default_factory=list)
    
    def add_actual_result(self, result: EvalResult) -> None:
        """Add an actual evaluation result to this trial."""
        self.actual_results.append(result)
    
    def get_trial_count(self) -> int:
        """Get the number of actual results collected for this trial."""
        return len(self.actual_results)
    
    def clear_actual_results(self) -> None:
        """Clear all actual results from this trial."""
        self.actual_results.clear()


@dataclass
class EvalTrialSuite:
    """A collection of evaluation trials with specified run counts."""
    trials: Dict[str, EvalTrial] = field(default_factory=dict)
    trial_run_counts: Dict[str, int] = field(default_factory=dict)
    
    def add_trial(self, trial: EvalTrial, run_count: int = 1) -> None:
        """
        Add a trial to the suite with a specified number of runs.
        
        Args:
            trial: The EvalTrial to add
            run_count: Number of times this trial should be run (default: 1)
        """
        self.trials[trial.clip_name] = trial
        self.trial_run_counts[trial.clip_name] = run_count
    
    def get_trial(self, clip_name: str) -> Optional[EvalTrial]:
        """Get a trial by clip name."""
        return self.trials.get(clip_name)
    
    def get_run_count(self, clip_name: str) -> int:
        """Get the number of times a trial should be run."""
        return self.trial_run_counts.get(clip_name, 0)
    
    def get_all_trials(self) -> Dict[str, EvalTrial]:
        """Get all trials in the suite."""
        return self.trials.copy()
    
    def get_trial_names(self) -> List[str]:
        """Get list of all trial clip names."""
        return list(self.trials.keys())
    
    def remove_trial(self, clip_name: str) -> bool:
        """
        Remove a trial from the suite.
        
        Args:
            clip_name: Name of the clip trial to remove
            
        Returns:
            True if trial was removed, False if not found
        """
        if clip_name in self.trials:
            del self.trials[clip_name]
            del self.trial_run_counts[clip_name]
            return True
        return False
    
    def clear_all_results(self) -> None:
        """Clear all actual results from all trials."""
        for trial in self.trials.values():
            trial.clear_actual_results()
    
    def get_total_expected_runs(self) -> int:
        """Get the total number of expected runs across all trials."""
        return sum(self.trial_run_counts.values())
    
    def get_completed_runs(self) -> int:
        """Get the total number of completed runs across all trials."""
        return sum(trial.get_trial_count() for trial in self.trials.values())
    
    def is_suite_complete(self) -> bool:
        """Check if all trials have completed their required number of runs."""
        for clip_name, trial in self.trials.items():
            if trial.get_trial_count() < self.get_run_count(clip_name):
                return False
        return True
