"""
Example script demonstrating how to retrieve a task from TaskHub API.
"""
import requests

# API Configuration
BASE_URL = "https://hackbay-backend-staging.sisung-kim1.workers.dev/api/tasks"
API_TOKEN = "your-api-token"  # Replace with your actual token

# Request Headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

def get_task(user_id: str, task_name: str, include_files: bool = True):
    """Retrieve a task from TaskHub.
    
    Args:
        user_id: ID of the task owner
        task_name: Name of the task
        include_files: Whether to include file contents in response
    """
    try:
        # Build URL with query parameters
        url = f"{BASE_URL}/{user_id}/{task_name}"
        params = {"files": "true" if include_files else "false"}
        
        # Make GET request
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        task_data = response.json()
        
        # Print task details
        print(f"\nTask: {user_id}/{task_name}")
        print("\nMetadata:")
        for key, value in task_data["metadata"].items():
            print(f"  {key}: {value}")
            
        if include_files and "files" in task_data:
            print("\nFiles:")
            for filename, content in task_data["files"].items():
                print(f"\n{filename}:")
                print("-" * len(filename))
                print(content)
                
        return task_data
        
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving task: {str(e)}")
        if hasattr(e.response, 'json'):
            try:
                error_data = e.response.json()
                print(f"Error details: {error_data}")
            except ValueError:
                pass
        return None

if __name__ == "__main__":
    # Example usage
    get_task("user456", "hello-world-python") 