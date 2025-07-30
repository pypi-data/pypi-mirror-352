"""
Test cases for hello world implementation.
"""
import pytest
from hello import say_hello

def test_default_greeting():
    """Test the default greeting."""
    assert say_hello() == "Hello, World!"

def test_custom_greeting():
    """Test greeting with custom name."""
    assert say_hello("TaskHub") == "Hello, TaskHub!"

def test_empty_name():
    """Test greeting with empty name."""
    assert say_hello("") == "Hello, !" 