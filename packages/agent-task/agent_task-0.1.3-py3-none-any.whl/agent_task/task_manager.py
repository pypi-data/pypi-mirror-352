"""
Task management functionality for the AI Agent Platform.
"""
from pathlib import Path
from typing import Dict, List, Optional
import shutil
import yaml
import json
import re
import os
import requests
import subprocess

from .paths import (
    ensure_app_dirs,
    get_task_dir,
    init_task_dir,
    TASKS_DIR,
)
from .api import TaskHubAPI

class TaskManager:
    """Manages task creation, loading, and publishing."""
    
    @staticmethod
    def init_task(task_name: str) -> Path:
        """Initialize a new task structure.
        
        Args:
            task_name: Name of the task
            
        Returns:
            Path to the created task directory
        """
        # Create project directory in current working directory
        project_dir = Path.cwd() / task_name
        rules_dir = project_dir / "rules"
        mcp_dir = project_dir / "mcp"
        
        # Create directory structure
        for directory in [project_dir, rules_dir, mcp_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Create README.md
        readme_path = project_dir / "README.md"
        with open(readme_path, "w") as f:
            f.write(f"""# {task_name}

Task-specific AI configuration for Cursor AI.

## Structure

- `rules/` - Task-specific guidelines and rules
  - `rule.mdc` - Main rules file
- `mcp/` - Model Context Protocol servers
""")
        
        # Create rule.mdc
        rule_path = rules_dir / "rule.mdc"
        with open(rule_path, "w") as f:
            f.write(f"""# {task_name} Guidelines

## Description
Add your task-specific guidelines here.

## Rules
1. First guideline
2. Second guideline

## Examples
```python
# Example code or usage
print("Hello from {task_name}")
```
""")
        
        return project_dir
    
    @staticmethod
    def list_tasks() -> List[Dict[str, str]]:
        """List all available tasks.
        
        Returns:
            List of task information dictionaries
        """
        ensure_app_dirs()
        tasks = []
        
        for task_dir in TASKS_DIR.iterdir():
            if task_dir.is_dir():
                task_info = {
                    "name": task_dir.name,
                    "description": "",
                    "files": [],
                    "has_readme": False,
                    "has_rules": False,
                    "has_mcp": False,
                    "path": str(task_dir)
                }
                
                # Check README.md
                readme_path = task_dir / "README.md"
                if readme_path.exists():
                    task_info["has_readme"] = True
                    try:
                        with open(readme_path, 'r', encoding='utf-8') as f:
                            # Get first non-empty line after title
                            lines = f.readlines()
                            for line in lines[1:]:
                                if line.strip() and not line.startswith("#"):
                                    task_info["description"] = line.strip()
                                    break
                    except UnicodeDecodeError:
                        # Fallback to system default encoding if UTF-8 fails
                        with open(readme_path, 'r') as f:
                            lines = f.readlines()
                            for line in lines[1:]:
                                if line.strip() and not line.startswith("#"):
                                    task_info["description"] = line.strip()
                                    break
                
                # Check rules directory
                rules_dir = task_dir / "rules"
                if rules_dir.exists() and rules_dir.is_dir():
                    task_info["has_rules"] = True
                    for rule_file in rules_dir.glob("*.mdc"):
                        task_info["files"].append(f"rules/{rule_file.name}")
                
                # Check MCP directory
                mcp_dir = task_dir / "mcp"
                if mcp_dir.exists() and mcp_dir.is_dir():
                    task_info["has_mcp"] = True
                    for mcp_file in mcp_dir.glob("*.py"):
                        task_info["files"].append(f"mcp/{mcp_file.name}")
                
                # Check taskhub.yaml
                taskhub_path = task_dir / "taskhub.yaml"
                if taskhub_path.exists():
                    task_info["files"].append("taskhub.yaml")
                    try:
                        with open(taskhub_path, 'r', encoding='utf-8') as f:
                            yaml_content = yaml.safe_load(f)
                            if yaml_content:
                                task_info.update({
                                    "version": yaml_content.get("version", "0.1.0"),
                                    "author": yaml_content.get("author", ""),
                                    "license": yaml_content.get("license", "MIT"),
                                    "tags": yaml_content.get("tags", [])
                                })
                    except Exception:
                        pass
                
                tasks.append(task_info)
        
        return tasks
    
    @staticmethod
    def load_task(task_name: str, target_dir: Optional[Path] = None) -> None:
        """Load a task into the current project.
        
        Args:
            task_name: Name of the task to load
            target_dir: Directory to load the task into (default: current directory)
        """
        task_dir = get_task_dir(task_name)
        if not task_dir.exists():
            raise ValueError(f"Task '{task_name}' not found")
        
        if target_dir is None:
            target_dir = Path.cwd()
        
        # Create task directory in target location
        target_task_dir = target_dir / task_name
        if target_task_dir.exists():
            raise ValueError(f"Directory '{task_name}' already exists in current location")
            
        # Copy entire task directory
        shutil.copytree(task_dir, target_task_dir)
        
        # Also set up .cursor directory for AI assistance
        cursor_dir = target_dir / ".cursor"
        cursor_dir.mkdir(exist_ok=True)
        
        # Copy rules to .cursor if they exist
        rules_src = task_dir / "rules"
        if rules_src.exists():
            rules_dst = cursor_dir / "rules"
            if rules_dst.exists():
                shutil.rmtree(rules_dst)
            shutil.copytree(rules_src, rules_dst)
        
        # Handle MCP servers
        mcp_src = task_dir / "mcp"
        if mcp_src.exists():
            # Create or load existing MCP config
            mcp_config_path = cursor_dir / "mcp.json"
            mcp_config = {
                "mcpServers": {}
            }
            if mcp_config_path.exists():
                with open(mcp_config_path, 'r', encoding='utf-8') as f:
                    try:
                        mcp_config = json.load(f)
                    except json.JSONDecodeError:
                        pass
            
            # Process each MCP server file
            for server_file in mcp_src.glob("*.py"):
                server_name = server_file.stem
                
                # Read the server file to extract API schema
                with open(server_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract server attributes
                name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
                instructions_match = re.search(r'instructions\s*=\s*["\']([^"\']+)["\']', content)
                tools_match = re.search(r'tools\s*=\s*\[(.*?)\]', content, re.DOTALL)
                
                if name_match:
                    server_name = name_match.group(1)
                
                # Create server config
                server_config = {
                    "command": "instant-mcp",
                    "args": [server_name],
                    "description": instructions_match.group(1) if instructions_match else "",
                    "tools": []
                }
                
                # Extract tools
                if tools_match:
                    tools_str = tools_match.group(1)
                    tools = [t.strip(' "\'') for t in tools_str.split(',') if t.strip()]
                    server_config["tools"] = tools
                
                # Add to config
                mcp_config["mcpServers"][server_name] = server_config
            
            # Save updated MCP config
            with open(mcp_config_path, 'w', encoding='utf-8') as f:
                json.dump(mcp_config, f, indent=2)
    
    @staticmethod
    def archive_task(task_name: str, remove_current: bool = False) -> None:
        """Archive task to Cursor AI configuration.
        
        Args:
            task_name: Name of the task to export
            remove_current: If True, removes the task files from current directory after archiving
        """
        # Ensure application directories exist
        ensure_app_dirs()
        
        # Get current directory contents
        current_dir = Path.cwd()
        task_folder = current_dir / task_name
        rules_dir = task_folder / "rules"
        mcp_dir = task_folder / "mcp"
        readme = task_folder / "README.md"
        
        # If no task files exist, create initial structure
        if not task_folder.exists():
            task_folder.mkdir(parents=True, exist_ok=True)
            rules_dir.mkdir(parents=True, exist_ok=True)
            mcp_dir.mkdir(parents=True, exist_ok=True)
            
            # Create initial rule.mdc file
            rule_path = rules_dir / "rule.mdc"
            with open(rule_path, "w", encoding='utf-8') as f:
                f.write(f"""# {task_name} Guidelines

## Description
Add your task-specific guidelines here.

## Rules
1. First guideline
2. Second guideline

## Examples
```python
# Example code or usage
print("Hello from {task_name}")
```
""")
            
            # Create initial README.md
            if not readme.exists():
                with open(readme, "w", encoding='utf-8') as f:
                    f.write(f"""# {task_name}

Task-specific AI configuration for Cursor AI.

## Structure

- `rules/` - Task-specific guidelines and rules
  - `rule.mdc` - Main rules file
- `mcp/` - Model Context Protocol servers
""")
        
        # Get or create task directory in app path
        app_task_dir = get_task_dir(task_name)
        app_task_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy rules if they exist
        if rules_dir.exists():
            rules_dst = app_task_dir / "rules"
            if rules_dst.exists():
                shutil.rmtree(rules_dst)
            shutil.copytree(rules_dir, rules_dst)
        
        # Copy MCP servers if they exist
        if mcp_dir.exists():
            mcp_dst = app_task_dir / "mcp"
            if mcp_dst.exists():
                shutil.rmtree(mcp_dst)
            shutil.copytree(mcp_dir, mcp_dst)
        
        # Copy README.md if it exists
        if readme.exists():
            shutil.copy2(readme, app_task_dir / "README.md")
        
        # Remove current task directory if requested
        if remove_current and task_folder.exists():
            shutil.rmtree(task_folder)
    
    @staticmethod
    def publish_task(task_name: str, user_id: str = "user456") -> str:
        """Publish task to marketplace."""
        # Find task directory
        task_dir = Path.cwd() / task_name
        if not task_dir.exists():
            task_dir = get_task_dir(task_name)
            if not task_dir.exists():
                raise ValueError(f"Task '{task_name}' not found")
        
        # Verify required files exist
        readme_path = task_dir / "README.md"
        taskhub_path = task_dir / "taskhub.yaml"
        if not readme_path.exists():
            raise ValueError(f"Required file README.md not found in {task_dir}")
        if not taskhub_path.exists():
            raise ValueError(f"Required file taskhub.yaml not found in {task_dir}")
        
        try:
            # Publish task
            api = TaskHubAPI()
            result = api.publish_task(task_dir, user_id)
            
            # Get URL from response
            if not result.get('url'):
                raise ValueError("Invalid response from server: missing URL")
            return result['url']
            
        except Exception as e:
            raise ValueError(f"Error publishing task: {str(e)}")
    
    @staticmethod
    def clone_task(url: str) -> str:
        """Clone a task from marketplace.
        
        Args:
            url: URL or path of the task to clone (e.g., user/task-name)
            
        Returns:
            Name of the cloned task
        """
        # Parse user ID and task name from URL
        parts = url.strip("/").split("/")
        if len(parts) != 2:
            raise ValueError("Invalid task URL. Expected format: user-id/task-name")
            
        user_id, task_name = parts
        
        # Initialize API client
        api = TaskHubAPI()
        
        # Get task with files
        task_data = api.get_task(user_id, task_name, include_files=True)
        
        # Ensure app directories exist
        ensure_app_dirs()
        
        # Create task directory
        task_dir = get_task_dir(task_name)
        task_dir.mkdir(parents=True, exist_ok=True)
        
        # Write README.md
        readme_path = task_dir / "README.md"
        with open(readme_path, "w", encoding="utf-8") as f:
            # Use readme content from task_data, or create a default one if not available
            readme_content = task_data.get("readme", f"# {task_name}\n\n{task_data.get('description', '')}")
            f.write(readme_content)
            
        # Write taskhub.yaml
        taskhub_path = task_dir / "taskhub.yaml"
        # Handle tags that could be either a string or list
        tags = task_data.get("tags", [])
        if isinstance(tags, str):
            tags = tags.split(",") if tags else []
            
        taskhub_config = {
            "name": task_name,
            "version": task_data.get("version", "0.1.0"),
            "description": task_data.get("description", ""),
            "author": task_data.get("userId", user_id),
            "license": task_data.get("license", "MIT"),
            "tags": tags
        }
        with open(taskhub_path, "w", encoding="utf-8") as f:
            yaml.dump(taskhub_config, f)
            
        # Write other files
        if "files" in task_data:
            for file_path, content in task_data["files"].items():
                full_path = task_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
                    
        return task_name 
    
    @staticmethod
    def import_task(task_name: str, target_dir: Optional[Path] = None) -> None:
        """Load a task into the current project.
        
        Args:
            task_name: Name of the task to load
            target_dir: Directory to load the task into (default: current directory)
        """

        task_dir = get_task_dir(task_name)
        if not task_dir.exists():
            raise ValueError(f"Task '{task_name}' not found")
        
        if target_dir is None:
            target_dir = Path.cwd()
        
        # Create .cursor directory if it doesn't exist
        cursor_dir = target_dir / ".cursor"
        cursor_dir.mkdir(exist_ok=True)
        
        # Copy rules
        rules_src = task_dir / "rules"
        rules_dst = cursor_dir / "rules"
        if rules_src.exists():
            if rules_dst.exists():
                shutil.rmtree(rules_dst)
            shutil.copytree(rules_src, rules_dst)
        
        # Handle MCP servers
        mcp_src = task_dir / "mcp"

        print(f"MCP src: {mcp_src}")
        print(f"MCP dst: {target_dir}")

        if mcp_src.exists():
            # Use instant-mcp to configure and export MCP servers
            try:
                # Set the MCP servers directory
                subprocess.run(["instant-mcp", "config:set-target-path", str(mcp_src)], check=True)
                
                # Export the configuration to the target directory
                subprocess.run(["instant-mcp", "export:cursor", "--output", str(target_dir)], check=True)
                
            except subprocess.CalledProcessError as e:
                print(f"Error configuring MCP servers: {e}")
                raise
    