"""
Configuration module for the EasyGit CLI
"""

import os
import json
from typing import Dict, Any, Optional

CONFIG_DIR = os.path.expanduser("~/.config/easy-git")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def ensure_config_dir() -> None:
    """Ensure the configuration directory exists."""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)

def load_config() -> Dict[str, Any]:
    """Load the configuration from the config file."""
    ensure_config_dir()
    
    if not os.path.exists(CONFIG_FILE):
        return {}
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_config(config: Dict[str, Any]) -> None:
    """Save the configuration to the config file."""
    ensure_config_dir()
    
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except IOError:
        pass

def get_config_value(key: str, default: Any = None) -> Any:
    """Get a value from the configuration."""
    config = load_config()
    return config.get(key, default)

def set_config_value(key: str, value: Any) -> None:
    """Set a value in the configuration."""
    config = load_config()
    config[key] = value
    save_config(config)
