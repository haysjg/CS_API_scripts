"""Authentication utilities for FalconPy."""

import os
import json
from pathlib import Path
from typing import Dict, Optional, Tuple
from falconpy import OAuth2


def load_credentials_from_env() -> Optional[Dict[str, str]]:
    """
    Load Falcon API credentials from environment variables.

    Returns:
        Dict containing client_id, client_secret, and base_url if found, None otherwise
    """
    client_id = os.getenv("FALCON_CLIENT_ID")
    client_secret = os.getenv("FALCON_CLIENT_SECRET")
    base_url = os.getenv("FALCON_BASE_URL", "https://api.crowdstrike.com")

    if client_id and client_secret:
        return {
            "client_id": client_id,
            "client_secret": client_secret,
            "base_url": base_url
        }

    return None


def load_credentials_from_file(config_path: str) -> Dict[str, str]:
    """
    Load Falcon API credentials from a JSON configuration file.

    Args:
        config_path: Path to the credentials JSON file

    Returns:
        Dict containing client_id, client_secret, and optional base_url

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If required fields are missing
    """
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_file, "r") as f:
        credentials = json.load(f)

    required_fields = ["client_id", "client_secret"]
    missing_fields = [field for field in required_fields if field not in credentials]

    if missing_fields:
        raise ValueError(f"Missing required fields in config: {', '.join(missing_fields)}")

    # Set default base_url if not provided
    if "base_url" not in credentials:
        credentials["base_url"] = "https://api.crowdstrike.com"

    return credentials


def get_credentials_smart(
    config_path: Optional[str] = None,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    base_url: str = "https://api.crowdstrike.com"
) -> Tuple[Optional[str], Optional[str], str, str]:
    """
    Get Falcon API credentials with smart fallback logic.

    Priority order:
    1. Config file (if provided)
    2. CLI arguments (if provided)
    3. Environment variables (if available)

    Args:
        config_path: Path to credentials JSON file
        client_id: Client ID from CLI
        client_secret: Client Secret from CLI
        base_url: Base URL (default: https://api.crowdstrike.com)

    Returns:
        Tuple of (client_id, client_secret, base_url, source)
        source is one of: "config_file", "cli_args", "env_vars", or "none"
    """
    # Priority 1: Config file
    if config_path:
        try:
            creds = load_credentials_from_file(config_path)
            return (
                creds["client_id"],
                creds["client_secret"],
                creds.get("base_url", base_url),
                "config_file"
            )
        except Exception as e:
            # If config file fails, continue to next method
            pass

    # Priority 2: CLI arguments
    if client_id and client_secret:
        return (client_id, client_secret, base_url, "cli_args")

    # Priority 3: Environment variables
    env_creds = load_credentials_from_env()
    if env_creds:
        return (
            env_creds["client_id"],
            env_creds["client_secret"],
            env_creds["base_url"],
            "env_vars"
        )

    # No credentials found
    return (None, None, base_url, "none")


def get_credentials(config_path: Optional[str] = None) -> Dict[str, str]:
    """
    Get Falcon API credentials from file or environment variables.

    DEPRECATED: Use get_credentials_smart() instead for better control.

    Args:
        config_path: Optional path to credentials file. If not provided,
                    will attempt to load from environment variables.

    Returns:
        Dict containing client_id, client_secret, and base_url
    """
    if config_path:
        return load_credentials_from_file(config_path)
    else:
        env_creds = load_credentials_from_env()
        if env_creds:
            return env_creds
        raise ValueError("No credentials found in environment variables")


def create_auth_object(config_path: Optional[str] = None) -> OAuth2:
    """
    Create and return an authenticated OAuth2 object.

    Args:
        config_path: Optional path to credentials file

    Returns:
        Authenticated OAuth2 object

    Raises:
        Exception: If authentication fails
    """
    creds = get_credentials(config_path)

    auth = OAuth2(
        client_id=creds["client_id"],
        client_secret=creds["client_secret"],
        base_url=creds["base_url"]
    )

    # Test authentication
    if not auth.token()['status_code'] == 201:
        raise Exception("Authentication failed. Please check your credentials.")

    return auth
