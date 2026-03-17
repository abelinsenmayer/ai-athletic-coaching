#!/usr/bin/env python3
"""
Test runner for video clip evaluation system.
"""

import argparse
import json
import sys
from pathlib import Path

from src.evaluation.eval_result import EvalResult
from src.evaluation.evaluate_clip import evaluateClip
from src.evaluation.grade_evaluation import gradeEvaluation
from src.ollama.ollama_prompt import ollama_prompt


def parse_eval_file(eval_path: Path) -> EvalResult:
    """
    Parse an evaluation file and return an EvalResult.
    
    Args:
        eval_path: Path to the evaluation file
        
    Returns:
        EvalResult: Parsed evaluation result
    """
    with open(eval_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return EvalResult(
        score=data.get('score', 0.0),
        feedbackText=data.get('feedbackText', '')
    )


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


def main():
    """Main function for the test runner."""
    parser = argparse.ArgumentParser(description='Test video clip evaluation system')
    parser.add_argument('root_dir', type=Path, help='Root directory containing clips and evals subdirectories')
    
    args = parser.parse_args()
    
    root_dir = args.root_dir.resolve()
    
    if not root_dir.exists():
        print(f"Error: Root directory {root_dir} does not exist")
        sys.exit(1)
    
    # Validate directory structure
    validate_directory_structure(root_dir)
    
    # Find clip-eval pairs
    pairs = find_clip_eval_pairs(root_dir)
    
    if not pairs:
        print("No clip-eval pairs found")
        sys.exit(1)
    
    print(f"Found {len(pairs)} clip-eval pairs")
    
    # Process each pair
    grades = []
    assessment_texts = []
    for clip_path, eval_path in pairs:
        print(f"\nProcessing: {clip_path.name}")
        
        # Parse expected result from eval file
        expected_result = parse_eval_file(eval_path)
        
        # Evaluate the clip
        actual_result = evaluateClip(clip_path)
        
        # Grade the evaluation
        grade = gradeEvaluation(expected_result, actual_result)
        grades.append(grade)
        
        # Collect assessment text if available
        if grade.assessmentText:
            assessment_texts.append(grade.assessmentText)
    
    print(f"\nCompleted processing {len(pairs)} clips")
    
    # Calculate average grades
    if grades:
        avg_coaching_accuracy = sum(g.coachingAccuracy for g in grades) / len(grades)
        avg_feedback_relevance = sum(g.feedbackRelevance for g in grades) / len(grades)
        avg_coaching_tone = sum(g.coachingTone for g in grades) / len(grades)
        avg_score_accuracy = sum(g.scoreAccuracy for g in grades) / len(grades)
        print(f"\n=== AVERAGE GRADES ===")
        print(f"  Coaching accuracy: {avg_coaching_accuracy:.2f}/10")
        print(f"  Feedback relevance: {avg_feedback_relevance:.2f}/10")
        print(f"  Coaching tone: {avg_coaching_tone:.2f}/10")
        print(f"  Score accuracy: {avg_score_accuracy:.2f}/10")
        
        # Generate summary of assessment patterns using ollama
        if assessment_texts:
            print(f"\nGenerating feedback pattern summary...")
            
            # Load summary prompt from file
            summary_prompt_path = Path(__file__).parent.parent / "src" / "evaluation" / "prompts" / "summary_prompt.txt"
            try:
                with open(summary_prompt_path, 'r', encoding='utf-8') as f:
                    summary_prompt_template = f.read()
                
                summary_prompt = summary_prompt_template.format(
                    assessment_texts='---'.join(assessment_texts)
                )
                
                summary = ollama_prompt(summary_prompt)
                print(f"\n=== FEEDBACK PATTERN SUMMARY ===")
                print(summary)
                print("================================")
            except Exception as e:
                print(f"Error generating summary: {e}")


if __name__ == "__main__":
    main()
