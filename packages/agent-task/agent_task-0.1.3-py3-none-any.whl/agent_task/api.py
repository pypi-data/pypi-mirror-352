"""
API integration for TaskHub marketplace.
"""
from pathlib import Path
from typing import Dict
import requests
import yaml

class TaskHubAPI:
    """Client for interacting with the TaskHub API."""
    
    def __init__(self, base_url: str = "https://hackbay-backend-staging.sisung-kim1.workers.dev"):
        """Initialize the API client."""
        self.base_url = base_url.rstrip('/')
    
    def publish_task(self, task_dir: Path, user_id: str) -> Dict:
        """Upload a task to the TaskHub marketplace."""
        # Read task files
        with open(task_dir / "README.md", "r", encoding="utf-8") as f:
            readme_content = f.read()
            
        with open(task_dir / "taskhub.yaml", "r", encoding="utf-8") as f:
            taskhub_content = f.read()
            
        # Collect all files except README.md and taskhub.yaml
        files = {}
        for file_path in task_dir.rglob("*"):
            if file_path.is_file() and file_path.name not in ["README.md", "taskhub.yaml"]:
                rel_path = str(file_path.relative_to(task_dir)).replace("\\", "/")
                with open(file_path, "r", encoding="utf-8") as f:
                    files[rel_path] = f.read()
        
        # Prepare request data
        task_data = {
            "userId": user_id,
            "taskName": task_dir.name,
            "readme": readme_content,
            "taskhubYaml": taskhub_content,
            "files": files
        }
        
        try:
            # Make API request
            url = f"{self.base_url}/api/tasks"
            response = requests.post(
                url,
                json=task_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer your-api-token"
                }
            )
            
            # Handle common error cases
            if response.status_code == 404:
                raise ValueError(f"API endpoint not found: {url}")
            elif response.status_code == 400:
                error_data = response.json()
                raise ValueError(f"Bad request: {error_data.get('error', 'Unknown error')}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    raise ValueError(error_data.get('error', str(e)))
                except ValueError:
                    pass
            raise ValueError(f"API request failed: {str(e)}")
    
    def get_task(self, user_id: str, task_name: str, include_files: bool = False) -> Dict:
        """Get task details from the marketplace."""
        try:
            url = f"{self.base_url}/api/tasks/{user_id}/{task_name}"
            response = requests.get(
                url,
                params={'files': str(include_files).lower()},
                headers={
                    "Content-Type": "application/json"
                }
            )
            
            # Handle common error cases
            if response.status_code == 404:
                raise ValueError(f"Task not found: {user_id}/{task_name}")
            elif response.status_code == 400:
                error_data = response.json()
                raise ValueError(f"Bad request: {error_data.get('error', 'Unknown error')}")
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    raise ValueError(error_data.get('error', str(e)))
                except ValueError:
                    pass
            raise ValueError(f"API request failed: {str(e)}") 