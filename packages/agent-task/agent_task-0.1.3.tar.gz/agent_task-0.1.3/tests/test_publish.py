import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import requests

from agent_task.api import TaskHubAPI

@pytest.fixture
def sample_task_dir(tmp_path):
    """Create a temporary task directory with required files for testing."""
    task_dir = tmp_path / "test_task"
    task_dir.mkdir()
    
    # Create README.md
    readme_content = "# Test Task\nThis is a test task."
    with open(task_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    # Create a sample file
    with open(task_dir / "main.py", "w", encoding="utf-8") as f:
        f.write('print("Hello, World!")')
    
    return task_dir

@pytest.fixture
def api_client():
    """Create a TaskHubAPI instance."""
    return TaskHubAPI()

def test_publish_task(sample_task_dir, api_client):
    """Test task publication."""
    user_id = "test_user"
    expected_response = {
        "success": True,
        "taskId": "123",
        "url": "https://taskhub.dev/tasks/test_user/test_task"
    }
    
    # Mock the requests.post method
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_post.return_value = mock_response
        
        # Call publish_task
        result = api_client.publish_task(sample_task_dir, user_id)
        
        # Verify the result
        assert result == expected_response
        
        # Verify the API was called with correct data
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        
        # Check payload
        payload = call_args[1]['json']
        assert payload['userId'] == user_id
        assert payload['taskName'] == "test_task"
        assert isinstance(payload['readme'], str)
        assert isinstance(payload['taskhubYaml'], str)
        assert isinstance(payload['files'], dict)
        assert "main.py" in payload["files"]

def test_get_task(api_client):
    """Test task retrieval."""
    user_id = "test_user"
    task_name = "test_task"
    expected_response = {
        "metadata": {
            "id": "123",
            "user_id": user_id,
            "task_name": task_name,
            "title": "Test Task"
        }
    }
    
    # Mock the requests.get method
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        # Call get_task
        result = api_client.get_task(user_id, task_name)
        
        # Verify the result
        assert result == expected_response
        
        # Verify the API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        
        # Check URL and params
        assert f"/api/tasks/{user_id}/{task_name}" in call_args[0][0]
        assert call_args[1]['params'] == {'files': 'false'} 