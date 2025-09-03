"""Utility to load environment variables."""
from dotenv import load_dotenv

def load_env():
    """
    Loads environment variables from a .env file in the project root.
    """
    load_dotenv()
