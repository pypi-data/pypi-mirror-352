"""
A simple Hello World implementation.
"""

def say_hello(name: str = "World") -> str:
    """
    Returns a hello message for the given name.
    
    Args:
        name: Name to greet (defaults to "World")
        
    Returns:
        A greeting message
    """
    return f"Hello, {name}!"

def main():
    """Main entry point."""
    message = say_hello()
    print(message)

if __name__ == "__main__":
    main() 