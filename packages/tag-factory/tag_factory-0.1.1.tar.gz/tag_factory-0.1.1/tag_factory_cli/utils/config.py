"""
Configuration utilities for Tag Factory CLI.
"""
import os
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".tag-factory"
CONFIG_FILE = CONFIG_DIR / "config.json"

class Config:
    """Configuration handler for Tag Factory CLI."""

    def __init__(self):
        """Initialize configuration handler using environment variables and config file."""
        self.ensure_config_dir()
        self.config = self.load_config()

    def ensure_config_dir(self):
        """Ensure configuration directory exists."""
        CONFIG_DIR.mkdir(exist_ok=True)
        if not CONFIG_FILE.exists():
            self.save_config({
                "api_key": os.environ.get("TAG_FACTORY_API_KEY", ""),
                "api_url": os.environ.get("TAG_FACTORY_API_URL", ""),
                "current_workspace": None
            })

    def load_config(self):
        """Load configuration from file."""
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # ファイルが存在しないか、不正なJSONの場合は空の設定を返す
            return {}

    def save_config(self, config):
        """Save configuration to file."""
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)

    def get(self, key, default=None):
        """Get configuration value from environment variable or config file.
        
        Args:
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        env_key = f"TAG_FACTORY_{key.upper()}"
        # 環境変数が優先
        return os.environ.get(env_key) or self.config.get(key, default)

    def set(self, key, value):
        """Set configuration value in config file.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
        self.save_config(self.config)

    def get_api_key(self):
        """Get API key from environment variable or config file."""
        return os.environ.get("TAG_FACTORY_API_KEY") or self.config.get("api_key")

    def get_api_url(self):
        """Get API URL from environment variable or config file."""
        return os.environ.get("TAG_FACTORY_API_URL") or self.config.get("api_url", "http://localhost:3000/api/cli")

    def get_current_workspace(self):
        """Get current workspace ID."""
        return self.config.get("current_workspace")

    def set_current_workspace(self, workspace_id):
        """Set current workspace ID."""
        self.config["current_workspace"] = workspace_id
        self.save_config(self.config)
