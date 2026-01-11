"""Configuration management for imggen"""

import json
import os
import stat
import sys
from pathlib import Path
from getpass import getpass

# Default configuration
DEFAULT_PROVIDER = "openai"


def get_config_dir():
    """Get config directory for imggen."""
    config_home = os.getenv("XDG_CONFIG_HOME", str(Path.home() / ".config"))
    config_dir = Path(config_home) / "imggen"
    config_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(config_dir, stat.S_IRWXU)  # 0o700 - rwx for owner only
    return config_dir


def get_config_file():
    """Get config file path."""
    return get_config_dir() / "config.json"


def load_config():
    """Load config from config.json, handle migration from old format."""
    config_file = get_config_file()
    if config_file.exists():
        try:
            with open(config_file) as f:
                config = json.load(f)

            # Migrate old format: {"api_key": "..."} -> {"api_keys": {"google": "..."}}
            if "api_key" in config and "api_keys" not in config:
                api_key = config.pop("api_key")
                config["api_keys"] = {"google": api_key}
                config["default_provider"] = "google"
                save_config(config)

            return config
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_config(config):
    """Save config to config.json."""
    config_file = get_config_file()
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    os.chmod(config_file, stat.S_IRUSR | stat.S_IWUSR)  # 0o600 - rw for owner only


def get_api_keys() -> dict:
    """Get all API keys from config.

    Returns:
        Dict of provider -> api_key mappings
    """
    config = load_config()
    return config.get("api_keys", {})


def get_api_key_for_provider(provider_name: str) -> str:
    """Get API key for specific provider, prompt if missing.

    Args:
        provider_name: "google" or "openai"

    Returns:
        API key for the provider

    Raises:
        SystemExit: If user declines to provide key
    """
    api_keys = get_api_keys()

    if provider_name in api_keys and api_keys[provider_name]:
        return api_keys[provider_name]

    # Prompt for missing key
    print(f"\n🔑 {provider_name.upper()} API Key Required\n")
    if provider_name == "google":
        print("Get your key from: https://aistudio.google.com/api-keys")
    elif provider_name == "openai":
        print("Get your key from: https://platform.openai.com/api-keys")

    api_key = getpass(f"Enter your {provider_name.upper()} API key: ").strip()

    if not api_key:
        print("Error: API key cannot be empty")
        sys.exit(1)

    # Save to config
    config = load_config()
    if "api_keys" not in config:
        config["api_keys"] = {}
    config["api_keys"][provider_name] = api_key
    save_config(config)

    print(f"\n✓ API key saved to {get_config_file()}\n")
    return api_key


def get_api_key():
    """Get API key for default provider.

    Backward compatibility function that uses default provider.

    Returns:
        API key for the default provider
    """
    config = load_config()
    default_provider = config.get("default_provider", DEFAULT_PROVIDER)
    return get_api_key_for_provider(default_provider)


def setup_interactive():
    """Interactive setup wizard for multiple providers."""
    print("\n=== imggen Setup ===\n")

    config = load_config()
    if "api_keys" not in config:
        config["api_keys"] = {}

    # Setup Google
    print("Configure Google/Gemini API:")
    print("Get your key from: https://aistudio.google.com/api-keys")
    google_key = getpass("Enter your Google API key (or press Enter to skip): ").strip()
    if google_key:
        config["api_keys"]["google"] = google_key

    # Setup OpenAI
    print("\nConfigure OpenAI API:")
    print("Get your key from: https://platform.openai.com/api-keys")
    openai_key = getpass("Enter your OpenAI API key (or press Enter to skip): ").strip()
    if openai_key:
        config["api_keys"]["openai"] = openai_key

    # Set default provider
    if not google_key and not openai_key:
        print("\nError: At least one API key is required")
        return False

    if openai_key:
        config["default_provider"] = "openai"
    elif google_key:
        config["default_provider"] = "google"

    save_config(config)

    print(f"\n✓ Setup complete!")
    print(f"✓ Config saved to {get_config_file()}\n")
    return True
