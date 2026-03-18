#!/usr/bin/env python3
"""
Google Gemini AI evaluator for video clips.
"""

import time
from pathlib import Path
from google import genai
from google.genai import types

from ..evaluation.eval_result import EvalResult
from ..exercise.criterion import Importance

GEMINI_MODEL = "gemini-3.1-flash-lite-preview"


def _build_prompt_from_exercise(exercise) -> str:
    """Build evaluation prompt from Exercise criteria using template file."""
    # Read prompt template
    prompt_path = Path(__file__).parent / "prompts" / "evaluation_prompt.txt"
    with open(prompt_path, 'r', encoding='utf-8') as f:
        template = f.read().strip()
    
    # Build criteria sections
    high_criteria = exercise.get_criteria_by_importance(Importance.HIGH)
    medium_criteria = exercise.get_criteria_by_importance(Importance.MEDIUM)
    low_criteria = exercise.get_criteria_by_importance(Importance.LOW)
    
    criteria_sections = ""
    
    if high_criteria:
        criteria_sections += "Critical features (failing to satisfy these will reduce final score by at least 6 each):\n"
        for criterion in high_criteria:
            criteria_sections += f"- {criterion.long_description}\n"
        criteria_sections += "\n"
    
    if medium_criteria:
        criteria_sections += "Important features (failing to satisfy these will reduce final score by at least 3 each):\n"
        for criterion in medium_criteria:
            criteria_sections += f"- {criterion.long_description}\n"
        criteria_sections += "\n"
    
    if low_criteria:
        criteria_sections += "Nice-to-have features (failing to satisfy these may or may not reduce final score, but they are nice to have):\n"
        for criterion in low_criteria:
            criteria_sections += f"- {criterion.long_description}\n"
        criteria_sections += "\n"
    
    # Format template with exercise data
    return template.format(
        exercise_name=exercise.name.lower(),
        criteria_sections=criteria_sections.strip()
    )

def evaluate_video_with_gemini(video_path: str, exercise_file_path: str = None) -> EvalResult:
    """
    Evaluate a video clip using Google's Gemini model.
    For this to work, the API key must be set in the environment variable GEMINI_API_KEY.
    
    Args:
        video_path: Path to the video file to evaluate
        exercise_file_path: Path to JSON file containing exercise definition
        
    Returns:
        EvalResult with score (0-10) and qualitative feedback
    """
    client = genai.Client()

    # Upload video file
    video_file = client.files.upload(file=video_path)

    #Wait for processing (important for video!)
    while video_file.state == "PROCESSING":
        print("Processing video...")
        time.sleep(5)
        video_file = client.files.get(name=video_file.name)

    # Prompt the model to evaluate the video
    if exercise_file_path:
        from ..exercise.exercise import Exercise
        exercise = Exercise.from_json(exercise_file_path)
        prompt = _build_prompt_from_exercise(exercise)
    else:
        prompt_path = Path(__file__).parent / "prompts" / "evaluation_prompt.txt"
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt = f.read().strip()

    # Configure for low-cost video analysis
    config = types.GenerateContentConfig(
        media_resolution=types.MediaResolution.MEDIA_RESOLUTION_LOW
    )


    # Analyze with Gemini 3 Flash
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[
            video_file,
            prompt,
        ],
        config=config
    )
    
    # Parse the response using EvalResult's parsing method
    try:
        return EvalResult.from_llm_response(response.text)
    except ValueError as e:
        raise RuntimeError(f"Failed to parse AI response: {response.text}") from e
