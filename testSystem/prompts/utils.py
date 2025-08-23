from pathlib import Path

def load_prompt(prompt_path: str) -> str:
    """
    Loads a prompt from the specified path within the testSystem prompts directory.
    
    Args:
        prompt_path: The relative path to the prompt file from the 'testSystem/prompts' directory.
                     e.g., 'reporting/detailed_report.prompt'
        
    Returns:
        The content of the prompt file as a string.
    """
    # This file is in testSystem/prompts/utils.py
    # PROMPTS_DIR is testSystem/prompts
    PROMPTS_DIR = Path(__file__).resolve().parent
    full_path = PROMPTS_DIR / prompt_path
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # In a real app, you'd use a logger. For now, raising is clear.
        print(f"Error: Prompt file not found at: {full_path}")
        raise
    except Exception as e:
        print(f"Error reading prompt file at: {full_path}: {e}")
        raise IOError(f"Error reading prompt file at: {full_path}: {e}") 