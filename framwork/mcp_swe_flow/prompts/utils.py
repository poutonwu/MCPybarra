from pathlib import Path
import os
from jinja2 import Template

# This will be framwork/mcp_swe_flow/prompts/utils.py
# We need to calculate the project root relative to this file's location.
# The path is MCPServer-Generator/framwork/mcp_swe_flow/prompts/utils.py
# So we need to go up 4 levels.
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PROMPTS_DIR = PROJECT_ROOT / "framwork" / "mcp_swe_flow" / "prompts"

def load_prompt(prompt_path: str) -> Template:
    """
    Loads a prompt from the specified path within the prompts directory
    and returns it as a Jinja2 Template object.
    
    Args:
        prompt_path: The relative path to the prompt file from the 'prompts' directory.
                     e.g., 'swe_generator/api_spec_mode.prompt'
        
    Returns:
        The content of the prompt file as a Jinja2 Template object.
    """
    full_path = PROMPTS_DIR / prompt_path
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            prompt_content = f.read()
            return Template(prompt_content)
    except FileNotFoundError:
        # In a real app, you'd use a logger. For now, raising is clear.
        print(f"Error: Prompt file not found at: {full_path}")
        raise
    except Exception as e:
        print(f"Error reading prompt file at: {full_path}: {e}")
        raise IOError(f"Error reading prompt file at: {full_path}: {e}") 