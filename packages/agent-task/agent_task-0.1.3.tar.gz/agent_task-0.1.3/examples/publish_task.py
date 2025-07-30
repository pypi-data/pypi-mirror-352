"""
Example script demonstrating how to use the TaskHub API to publish a task.
"""
import requests

# API Configuration
API_URL = "https://hackbay-backend-staging.sisung-kim1.workers.dev/api/tasks"
API_TOKEN = "your-api-token"  # Replace with your actual token

# Request Headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

# Example task data
task_data = {
    "userId": "user456",
    "taskName": "hello-world-python-test",
    "readme": """# Hello World

Simple hello world example using Python.""",
    "taskhubYaml": """name: hello-world
version: '1.0.0'
author: Test User
description: Hello world task""",
    "files": {
        "hello.py": 'print("Hello, World!")'
    }
}

def publish_task():
    """Publish a task to TaskHub."""
    try:
        response = requests.post(API_URL, json=task_data, headers=headers)
        response.raise_for_status()  # Raise an exception for error status codes
        
        result = response.json()
        print("Task published successfully!")
        print(f"Task URL: {result.get('url')}")
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"Error publishing task: {str(e)}")
        if hasattr(e.response, 'json'):
            try:
                error_data = e.response.json()
                print(f"Error details: {error_data}")
            except ValueError:
                pass
        return None

if __name__ == "__main__":
    publish_task() 