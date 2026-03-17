#!/usr/bin/env python3
"""
Google Gemini AI evaluator for video clips.
"""

import time
from pathlib import Path
from google import genai
from google.genai import types

from ..evaluation.eval_result import EvalResult

GEMINI_MODEL = "gemini-3.1-flash-lite-preview"

def evaluate_video_with_gemini(video_path: str) -> EvalResult:
    """
    Evaluate a video clip using Google's Gemini model.
    For this to work, the API key must be set in the environment variable GEMINI_API_KEY.
    
    Args:
        video_path: Path to the video file to evaluate
        
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
    
    # Parse the response to extract score and feedback
    try:
        lines = response.text.strip().split('\n')
        if len(lines) >= 2:
            # First line should be the score
            score = float(lines[0].strip())
            # Rest of the lines are the feedback
            feedback = '\n'.join(lines[1:]).strip()
        else:
            raise ValueError("Response doesn't have enough lines")
    except (ValueError, IndexError) as e:
        raise RuntimeError(f"Failed to parse AI response: {response.text}") from e
    
    # Ensure score is within valid range
    score = max(0.0, min(10.0, score))
    
    return EvalResult(score=score, feedbackText=feedback)
