#!/usr/bin/env python3
"""
Generic Gemini prompt utility for sending text prompts to Google's Gemini model.
"""

from google import genai

GEMINI_MODEL = "gemini-3.1-flash-lite-preview"


def prompt_gemini(prompt: str) -> str:
    """
    Send a generic text prompt to Gemini and return the response.
    
    Args:
        prompt: The text prompt to send to Gemini
        
    Returns:
        str: The text response from Gemini
        
    Raises:
        RuntimeError: If the API call fails or response is empty
    """
    client = genai.Client()
    
    # Generate content with the prompt
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )
    
    if not response.text:
        raise RuntimeError("Empty response from Gemini")
    
    return response.text
