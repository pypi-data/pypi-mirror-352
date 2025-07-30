"""
Path management for the AI Agent Platform.
"""
from pathlib import Path
from typing import Final

from appdirs import AppDirs

# Initialize appdirs with our app info
APPNAME: Final[str] = "agent-task"
APPAUTHOR: Final[str] = "microwiseai"
dirs = AppDirs(APPNAME, APPAUTHOR)

# Application directories
APP_DIR: Final[Path] = Path(dirs.user_data_dir)
CONFIG_DIR: Final[Path] = Path(dirs.user_config_dir)
CACHE_DIR: Final[Path] = Path(dirs.user_cache_dir)
LOG_DIR: Final[Path] = Path(dirs.user_log_dir)

# Task-specific directories
TASKS_DIR: Final[Path] = APP_DIR / "tasks"

def ensure_app_dirs() -> None:
    """Create all necessary application directories if they don't exist."""
    for directory in [APP_DIR, CONFIG_DIR, CACHE_DIR, LOG_DIR, TASKS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

def get_task_dir(task_name: str) -> Path:
    """Get the directory path for a specific task.
    
    Args:
        task_name: Name of the task
        
    Returns:
        Path to the task directory
    """
    return TASKS_DIR / task_name

def init_task_dir(task_name: str) -> Path:
    """Initialize a new task directory structure.
    
    Args:
        task_name: Name of the task
        
    Returns:
        Path to the created task directory
    """
    task_dir = get_task_dir(task_name)
    rules_dir = task_dir / "rules"
    mcp_dir = task_dir / "mcp-servers"
    
    # Create directory structure
    for directory in [task_dir, rules_dir, mcp_dir]:
        directory.mkdir(parents=True, exist_ok=True)
        
    return task_dir 