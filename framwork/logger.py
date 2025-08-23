import sys
from datetime import datetime
import json
from loguru import logger as _logger
from pathlib import Path
import threading
from typing import Dict, Tuple
import os


PROJECT_ROOT = Path(__file__).parent.parent # Adjust based on actual execution context

_print_level = "INFO"


def define_log_level(print_level="INFO", logfile_level="DEBUG", name: str = None):
    """Adjust the log level to above level"""
    global _print_level
    _print_level = print_level

    # Define log directory and ensure it exists
    log_dir = PROJECT_ROOT / "logs" / "single_run"
    log_dir.mkdir(parents=True, exist_ok=True)

    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d%H%M%S")
    log_name = (
        f"{name}_{formatted_date}" if name else formatted_date
    )  # Name a log with prefix name
    
    log_path = log_dir / f"{log_name}.log"

    _logger.remove()
    _logger.add(sys.stderr, level=print_level)
    _logger.add(log_path, level=logfile_level)
    return _logger


logger = define_log_level()

# ========== Structured Logging System ==========
class AgentJsonlLogger:
    """
    Structured logger, one jsonl file per Agent.
    Usage:
        agent_logger = get_agent_logger("SWE-Agent")
        agent_logger.log(event_type="tool_call", tool="save_file", input=..., output=...)
    """
    def __init__(self, agent_name: str, log_dir: Path = None):
        self.agent_name = agent_name
        self.log_dir = log_dir or (PROJECT_ROOT / "logs/agent_logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        # Fix timestamp format to avoid illegal Windows filename characters
        now = datetime.now()
        timestamp = now.strftime("%Y%m%dT%H%M%S")[:-3] + "Z"  # Precise to milliseconds
        self.log_path = self.log_dir / f"{agent_name}-{timestamp}.jsonl"
        # Initialize token counter
        self.token_counter = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "calls": 0
        }
        self._lock = threading.Lock()

    def log(self, event_type: str, **kwargs):
        """Log an event"""
        log_entry = {
            "timestamp": datetime.now().isoformat() + "Z",
            "agent": self.agent_name,
            "event": event_type,
        }
        log_entry.update(kwargs)
        
        # Track LLM token consumption, update cumulative count
        if event_type in ["llm_invoke", "llm_response"] and "usage_metadata" in kwargs:
            metadata = kwargs["usage_metadata"]
            # Update token counter
            if event_type == "llm_invoke" and "input_tokens" in metadata:
                self.token_counter["prompt_tokens"] += metadata.get("input_tokens", 0)
                self.token_counter["total_tokens"] += metadata.get("input_tokens", 0)
                self.token_counter["calls"] += 1
            elif event_type == "llm_response" and "output_tokens" in metadata:
                self.token_counter["completion_tokens"] += metadata.get("output_tokens", 0)
                self.token_counter["total_tokens"] += metadata.get("output_tokens", 0)
        
        with self._lock:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def get_llm_usage_summary(self) -> Tuple[int, float]:
        """Read and summarize LLM usage from log files.

        Returns:
            A tuple (total_tokens, total_cost)
        """
        total_tokens = 0
        total_cost = 0.0

        # Compatible with both old and new attribute names
        log_file_path = getattr(self, "log_path", None) or getattr(self, "log_file", None)
        if not log_file_path or not os.path.exists(log_file_path):
            return 0, 0.0

        with self._lock:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line)
                        # Compatible with new and old log formats
                        if log_entry.get("event_type") == "llm_token_usage" or log_entry.get("event") == "llm_token_usage":
                            # Handle new format
                            if "usage_metadata" in log_entry:
                                usage_metadata = log_entry.get("usage_metadata", {})
                                total_tokens += usage_metadata.get("total_tokens", 0)
                                total_cost += usage_metadata.get("total_cost", 0.0)
                            # Handle old format
                            elif "details" in log_entry and "usage_metadata" in log_entry["details"]:
                                usage_metadata = log_entry["details"]["usage_metadata"]
                                total_tokens += usage_metadata.get("total_tokens", 0)
                                total_cost += usage_metadata.get("total_cost", 0.0)
                            # Handle oldest format
                            elif "usage" in log_entry:
                                total_tokens += log_entry["usage"].get("total_tokens", 0)
                                total_cost += log_entry.get("cost", 0.0)
                    except (json.JSONDecodeError, KeyError):
                        continue
        
        return total_tokens, total_cost
    
    def log_llm_usage(self, call_id: str, model_name: str, 
                      prompt_tokens: int = None, completion_tokens: int = None, 
                      prompt_cost: float = None, completion_cost: float = None):
        """Method specifically for logging LLM usage"""
        total_tokens = 0
        if prompt_tokens is not None:
            total_tokens += prompt_tokens
        if completion_tokens is not None:
            total_tokens += completion_tokens
            
        # Build unified usage metadata
        usage_metadata = {
            "model": model_name,
            "input_tokens": prompt_tokens,
            "output_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "prompt_cost": prompt_cost,
            "completion_cost": completion_cost,
            "total_cost": (prompt_cost or 0) + (completion_cost or 0)
        }
        
        # Record to total counter
        self.token_counter["prompt_tokens"] += prompt_tokens or 0
        self.token_counter["completion_tokens"] += completion_tokens or 0
        self.token_counter["total_tokens"] += total_tokens
        self.token_counter["calls"] += 1
        
        # Add a token usage summary event
        self.log(event_type="llm_token_usage", 
                 call_id=call_id,
                 usage_metadata=usage_metadata)
        
        return usage_metadata

    def get_token_stats(self):
        """Get current Agent's token usage statistics"""
        return {
            "agent": self.agent_name,
            "token_usage": self.token_counter,
            "timestamp": datetime.now().isoformat() + "Z"
        }

# Factory method to get structured logger for specified Agent
_agent_logger_cache = {}
_loggers_lock = threading.Lock()

def get_agent_logger(agent_name: str) -> AgentJsonlLogger:
    """Get or create logger instance for specified Agent"""
    with _loggers_lock:
        if agent_name not in _agent_logger_cache:
            _agent_logger_cache[agent_name] = AgentJsonlLogger(agent_name)
        return _agent_logger_cache[agent_name]


if __name__ == "__main__":
    logger.info("Starting framworklication")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")

    # Structured logging test
    swe_logger = get_agent_logger("SWE-Agent")
    swe_logger.log(event_type="tool_call", tool="save_file", input={"file": "a.py"}, output="ok", task_id="demo-001")
    # Token consumption test
    swe_logger.log_llm_usage("test-call-1", "qwen-max", prompt_tokens=1000, completion_tokens=500, prompt_cost=0.02, completion_cost=0.01)
    print(swe_logger.get_token_stats())
    
    # Test the new get_llm_usage_summary function
    tokens, cost = swe_logger.get_llm_usage_summary()
    print(f"Total Tokens: {tokens}, Total Cost: ${cost:.6f}")
