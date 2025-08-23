import json
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List

from framwork.logger import logger

def find_api_file(resources_dir: Path, api_name: str) -> Optional[Path]:
    """Find the OpenAPI file (YAML or JSON) for a given API name."""
    api_dir = resources_dir / api_name
    if not api_dir.is_dir():
        logger.warning(f"API directory not found: {api_dir}")
        return None
    
    for ext in ["*.yaml", "*.yml", "*.json"]:
        files = list(api_dir.glob(ext))
        if files:
            logger.info(f"Found API spec file: {files[0]}")
            return files[0] # Return the first found file
            
    logger.warning(f"No OpenAPI spec file found for API '{api_name}' in {api_dir}")
    return None

def load_api_spec(file_path: Path) -> Optional[Dict[str, Any]]:
    """Load API specification from a YAML or JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            if file_path.suffix in [".yaml", ".yml"]:
                spec = yaml.safe_load(f)
            else:
                spec = json.load(f)
            logger.info(f"Successfully loaded API spec from: {file_path}")
            return spec
    except Exception as e:
        logger.error(f"Error loading API spec file {file_path}: {e}")
        return None

def load_mcp_doc(resources_dir: Path) -> Optional[str]:
    """Load the MCP documentation content."""
    mcp_doc_path = resources_dir / "mcp-server-doc.md"
    if not mcp_doc_path.exists():
        logger.error(f"MCP documentation file not found: {mcp_doc_path}")
        return None
    try:
        with open(mcp_doc_path, "r", encoding="utf-8") as f:
            content = f.read()
            logger.info(f"Successfully loaded MCP documentation from: {mcp_doc_path}")
            return content
    except Exception as e:
        logger.error(f"Error loading MCP documentation {mcp_doc_path}: {e}")
        return None

def read_file_content(file_path: Path) -> Optional[str]:
    """Reads the content of a file."""
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            logger.info(f"Successfully read file content from: {file_path}")
            return content
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None
        
def list_server_files(output_dir: Path) -> List[str]:
    """Lists all Python files in the specified directory."""
    if not output_dir.exists():
        logger.warning(f"Output directory does not exist: {output_dir}")
        return []
    return [file.name for file in output_dir.glob("*.py")]

def list_report_files(report_dir: Path) -> List[str]:
    """Lists all Markdown files in the specified directory."""
    if not report_dir.exists():
        logger.warning(f"Report directory does not exist: {report_dir}")
        return []
    return [file.name for file in report_dir.glob("*.md")] 