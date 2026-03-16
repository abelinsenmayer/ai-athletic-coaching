#!/usr/bin/env python3
"""
Ollama prompt script that takes a prompt and optionally a model name.
Uses gemma3:4b as the default model.
"""

import ollama


def ollama_prompt(prompt: str, model: str = "gemma3:4b") -> str:
    """
    Send a prompt to Ollama and get a response.
    
    Args:
        prompt: The prompt to send to the model
        model: The model to use (default: gemma3:4b)
        
    Returns:
        The model's response as a string
        
    Raises:
        Exception: If there's an error communicating with Ollama
    """
    try:
        response = ollama.generate(
            model=model,
            prompt=prompt
        )
        return response['response']
    except Exception as e:
        raise Exception(f"Error communicating with Ollama: {e}")


def main():
    """
    Command-line interface for the ollama_prompt function.
    """
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description="Send a prompt to Ollama and get a response",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ollama_prompt.py "What is the capital of France?"
  python ollama_prompt.py "Explain quantum computing" --model llama3
  python ollama_prompt.py "Write a poem about nature" --model gemma3:4b
        """
    )
    
    parser.add_argument(
        "prompt",
        help="The prompt to send to the model"
    )
    
    parser.add_argument(
        "--model", "-m",
        default="gemma3:4b",
        help="The model to use (default: gemma3:4b)"
    )
    
    args = parser.parse_args()
    
    try:
        print(f"Sending prompt to {args.model}...")
        print(f"Prompt: {args.prompt}")
        print("-" * 50)
        
        response = ollama_prompt(args.prompt, args.model)
        print(response)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
