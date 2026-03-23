#!/usr/bin/env python3
"""
Test runner for video clip evaluation system.
"""

import argparse
import json
import sys
import threading
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import os

from src.evaluation.eval_result import EvalResult
from src.evaluation.evaluate_clip import evaluateClip
from src.evaluation.grade_evaluation import gradeEvaluation, EvaluationGrade
from src.ollama.ollama_prompt import ollama_prompt
from src.exercise.exercise import Exercise
from tests.eval_trial import EvalTrial, EvalTrialSuite

# Global thread count for parallel execution
THREAD_COUNT = 10


def parse_eval_file(eval_path: Path) -> EvalResult:
    """
    Parse an evaluation file and return an EvalResult.
    
    Args:
        eval_path: Path to the evaluation file
        
    Returns:
        EvalResult: Parsed evaluation result
    """
    with open(eval_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    return EvalResult.from_llm_response(content)


def validate_directory_structure(root_dir: Path) -> None:
    """
    Validate that the required directory structure exists.
    
    Args:
        root_dir: Root directory path
        
    Raises:
        SystemExit: If required directories are missing
    """
    clips_dir = root_dir / 'clips'
    evals_dir = root_dir / 'evals'
    
    if not clips_dir.exists():
        print(f"Error: clips directory not found at {clips_dir}")
        sys.exit(1)
    
    if not evals_dir.exists():
        print(f"Error: evals directory not found at {evals_dir}")
        sys.exit(1)
    
    print(f"Validated directory structure at {root_dir}")


def find_clip_eval_pairs(root_dir: Path) -> list[tuple[Path, Path]]:
    """
    Find all clip-eval pairs in the directory structure.
    
    Args:
        root_dir: Root directory path
        
    Returns:
        List of tuples containing (clip_path, eval_path)
    """
    clips_dir = root_dir / 'clips'
    evals_dir = root_dir / 'evals'
    
    pairs = []
    
    # Find all video files in clips directory
    for clip_file in clips_dir.iterdir():
        if clip_file.is_file():
            # Construct expected eval file name
            eval_filename = f"{clip_file.stem}-eval.txt"
            eval_path = evals_dir / eval_filename
            
            if eval_path.exists():
                pairs.append((clip_file, eval_path))
            else:
                print(f"Warning: No eval file found for {clip_file.name}")
    
    return pairs


def create_trial_suite(root_dir: Path, exercise_name: str, run_count: int = 3) -> EvalTrialSuite:
    """
    Create an EvalTrialSuite from clip-eval pairs in the directory structure.
    
    Args:
        root_dir: Root directory containing clips and evals subdirectories
        run_count: Number of times each trial should be run (default: 3)
        
    Returns:
        EvalTrialSuite populated with trials for all clip-eval pairs
    """
    pairs = find_clip_eval_pairs(root_dir)
    template_video_path = f'./src/exercise/exercise_sources/{exercise_name}/template.mp4'
    print(f"Working directory: {os.getcwd()}")

    exercise = Exercise.create_from_sources(criteria_json_path=f"./src/exercise/exercise_sources/{exercise_name}/criteria.json", template_video_path=template_video_path)
    
    suite = EvalTrialSuite()
    
    for clip_path, eval_path in pairs:
        # Parse expected result from eval file
        expected_result = parse_eval_file(eval_path)
        
        # Create trial with clip name (without extension)
        clip_name = clip_path.stem
        trial = EvalTrial(
            clip_name=clip_name,
            expected_result=expected_result,
            actual_results=[],
            execise=exercise,
        )
        
        # Add trial to suite with specified run count
        suite.add_trial(trial, run_count)
    
    return suite


def run_single_trial(clip_path: Path, trial: EvalTrial) -> None:
    """
    Run a single evaluation trial and add the result to the trial.
    
    Args:
        clip_path: Path to the video clip file
        trial: EvalTrial object to store the result
    """
    try:
        # Evaluate the clip
        actual_result = evaluateClip(clip_path, trial.execise)
        
        # Add result to trial (thread-safe)
        trial.add_actual_result(actual_result)
        print(f"Completed trial for {trial.clip_name} (run {trial.get_trial_count()})")
    except Exception as e:
        print(f"Error running trial for {trial.clip_name}: {e}")


def main():
    """Main function for the test runner."""
    parser = argparse.ArgumentParser(description='Test video clip evaluation system')
    parser.add_argument('root_dir', type=Path, help='Root directory containing clips and evals subdirectories')
    parser.add_argument('--trials', type=int, default=1, help='Number of times each trial should be run (default: 1)')
    parser.add_argument('--exercise', type=str, help='Exercise name')
    
    args = parser.parse_args()
    
    root_dir = args.root_dir.resolve()
    exercise_name = args.exercise
    
    if not root_dir.exists():
        print(f"Error: Root directory {root_dir} does not exist")
        sys.exit(1)
    
    # Validate directory structure
    validate_directory_structure(root_dir)
    
    # Create trial suite
    suite = create_trial_suite(root_dir, exercise_name, args.trials)
    
    if not suite.get_all_trials():
        print("No clip-eval pairs found")
        sys.exit(1)
    
    print(f"Created trial suite with {len(suite.get_all_trials())} trials")
    print(f"Each trial will run {args.trials} times")
    print(f"Total expected runs: {suite.get_total_expected_runs()}")
    print(f"Using {THREAD_COUNT} threads for parallel execution")
    
    # Run trials in parallel
    clips_dir = root_dir / 'clips'
    
    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        # Submit all trial runs to the executor
        futures = []
        
        for clip_name, trial in suite.get_all_trials().items():
            clip_path = clips_dir / f"{clip_name}.mp4"  # Assuming mp4 extension
            
            # Submit the trial the required number of times
            for run_num in range(suite.get_run_count(clip_name)):
                future = executor.submit(run_single_trial, clip_path, trial)
                futures.append(future)
        
        # Wait for all futures to complete
        for future in as_completed(futures):
            try:
                future.result()  # This will raise any exceptions that occurred
            except Exception as e:
                print(f"Trial execution error: {e}")
    
    print(f"\nCompleted processing. Total runs completed: {suite.get_completed_runs()}")
    
    # Grade all trials and collect results
    all_grades: list[EvaluationGrade] = []
    for clip_name, trial in suite.get_all_trials().items():
        print(f"\nGrading trial: {clip_name}")
        print(f"  Runs completed: {trial.get_trial_count()}")
        
        # Grade each actual result against the expected result
        trial_grades = []
        for i, actual_result in enumerate(trial.actual_results):
            grade = gradeEvaluation(trial.expected_result, actual_result)
            trial_grades.append(grade)
            print(f"  Run {i+1} accuracy: {Decimal(grade.get_accuracy_percentage()):.2%}")
        
        all_grades.extend(trial_grades)
    
    # Calculate and display accuracy results
    if all_grades:
        # Calculate overall average accuracy
        overall_accuracies = [g.get_accuracy_percentage() for g in all_grades]
        avg_overall_accuracy = sum(overall_accuracies) / len(overall_accuracies)
        
        print(f"\n=== OVERALL ACCURACY ===")
        print(f"  Average accuracy: {Decimal(avg_overall_accuracy):.2%}")
        
        # Collect criterion-specific accuracies and off_by values
        criterion_accuracies = {}
        criterion_counts = {}
        criterion_off_by_sums = {}
        
        for grade in all_grades:
            for criterion_name, accuracy in grade.criterion_scores.items():
                if criterion_name not in criterion_accuracies:
                    criterion_accuracies[criterion_name] = 0.0
                    criterion_counts[criterion_name] = 0
                    criterion_off_by_sums[criterion_name] = 0.0
                criterion_accuracies[criterion_name] += float(accuracy)
                criterion_counts[criterion_name] += 1
                criterion_off_by_sums[criterion_name] += grade.criterion_off_by[criterion_name]
        
        # Calculate average accuracy and off_by for each criterion
        print(f"\n=== CRITERION-BY-CRITERION ACCURACY ===")
        for criterion_name in sorted(criterion_accuracies.keys()):
            avg_accuracy = criterion_accuracies[criterion_name] / criterion_counts[criterion_name]
            avg_off_by = criterion_off_by_sums[criterion_name] / criterion_counts[criterion_name]
            
            # Format off_by with sign and percentage
            off_by_str = f"{Decimal(avg_off_by):+.1%}" if avg_off_by != 0 else "0.0%"
            print(f"  {criterion_name}: {Decimal(avg_accuracy):.2%} (avg off by: {off_by_str})")
        
        print("=" * 50)


if __name__ == "__main__":
    main()
