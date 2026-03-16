#!/usr/bin/env python3
"""
Google Gemini AI evaluator for video clips.
"""

import json
import re
from pathlib import Path
from typing import Optional

from google import genai

from ..evaluation.eval_result import EvalResult

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

    # Analyze with Gemini 3 Flash
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[
            video_file,
            prompt,
        ]
    )
    
    # Parse the response to extract score and feedback
    try:
        # Try to extract JSON from the response
        json_match = re.search(r'\{[^}]+\}', response.text, re.DOTALL)
        if json_match:
            result_data = json.loads(json_match.group())
            score = float(result_data.get("score", 0.0))
            feedback = result_data.get("feedback", "No feedback provided")
        else:
            raise ValueError("No JSON found in AI response")
    except (json.JSONDecodeError, ValueError) as e:
        raise RuntimeError(f"Failed to parse AI response: {response.text}") from e
    
    # Ensure score is within valid range
    score = max(0.0, min(10.0, score))
    
    return EvalResult(score=score, feedbackText=feedback)
