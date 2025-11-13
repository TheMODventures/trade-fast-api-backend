import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def verify_api_key(provided_key: Optional[str]) -> bool:
    """
    Verify if the provided API key matches the one in environment

    Args:
        provided_key: The API key provided in the request

    Returns:
        bool: True if valid, False otherwise
    """
    if not provided_key:
        return False

    # Get the valid API key from environment
    valid_api_key = os.getenv("API_KEY")
    print("Valid API Key from Env:", valid_api_key)
    if not valid_api_key:
        # If no API key is configured, reject all requests
        return False

    # Check if provided key matches the environment key
    return provided_key == valid_api_key


def get_api_key_from_header(authorization_header: Optional[str]) -> Optional[str]:
    """
    Extract API key from Authorization header

    Expected format: "Bearer <api_key>"

    Args:
        authorization_header: The Authorization header value

    Returns:
        str: Extracted API key or None
    """
    if not authorization_header:
        return None

    parts = authorization_header.split()
    if len(parts) != 2:
        return None

    scheme, key = parts
    if scheme.lower() == "bearer":
        return key

    return None
