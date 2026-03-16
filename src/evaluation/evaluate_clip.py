#!/usr/bin/env python3
"""
Clip evaluation module for assessing video files.
"""

from pathlib import Path
from .eval_result import EvalResult
from ..google.genai_evaluator import evaluate_video_with_gemini


def evaluateClip(clip_path: Path) -> EvalResult:
    """
    Evaluate a video clip and return an EvalResult.
    
    Args:
        clip_path: Path to the video clip file
        
    Returns:
        EvalResult: Evaluation result with score and feedback
    """
    print(f"Evaluating clip: {clip_path}")
    
    # Use Google Gemini to evaluate the video
    return evaluate_video_with_gemini(str(clip_path))
