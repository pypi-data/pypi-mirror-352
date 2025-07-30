# Tell the users that they just implement functions as they have done,
# and determine the name of the server and functions for AI to use.

def write_later(text: str):
    """
    Write the text to a file later.
    """
    with open("later.txt", "a") as f:
        f.write(text)

name = "text_server"
['write_later']