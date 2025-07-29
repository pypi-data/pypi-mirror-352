"""Configuration management for TFQ0tool."""

import os
from pathlib import Path
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
  
    "version": "2.1.7",  
    "processing": {
        "chunk_size": 1024 * 1024,  # 1MB
        "max_file_size": 1024 * 1024 * 1024,  # 1GB
        "timeout": 300,  # 5 minutes
        "max_retries": 3
    },
    "threading": {
        "min_threads": 1,
        "max_threads": 8,
        "thread_timeout": 600  # 10 minutes
    },
    "logging": {
        "max_log_size": 10 * 1024 * 1024,  # 10MB
        "backup_count": 5,
        "log_dir": str(Path.home() / '.tfq0tool' / 'logs')
    },
    "output": {
        "default_suffix": "_extracted.txt",
        "min_free_space": 1024 * 1024 * 100  # 100MB
    },
    "supported_formats": [
        ".pdf", ".docx", ".doc", ".txt", ".rtf",
        ".xlsx", ".xls", ".csv", ".json", ".xml"
    ]
}

class Config:
    """Configuration manager for TFQ0tool."""
    
    def __init__(self):
        self.config_dir = Path.home() / '.tfq0tool'
        self.config_file = self.config_dir / 'config.json'
        self.settings = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    # Merge with defaults, preserving user settings
                    return self._merge_configs(DEFAULT_CONFIG, user_config)
            else:
                self._save_default_config()
                return DEFAULT_CONFIG.copy()
        except Exception as e:
            logger.warning(f"Error loading config: {e}. Using defaults.")
            return DEFAULT_CONFIG.copy()

    def _save_default_config(self) -> None:
        """Save default configuration to file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving default config: {e}")

    def _merge_configs(self, default: Dict, user: Dict) -> Dict:
        """Recursively merge user config with defaults."""
        merged = default.copy()
        for key, value in user.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        return merged

    def get(self, section: str, key: str = None) -> Any:
        """Get a configuration value."""
        try:
            if key is None:
                return self.settings[section]
            return self.settings[section][key]
        except KeyError:
            logger.warning(f"Config key not found: {section}.{key}")
            if key is None:
                return DEFAULT_CONFIG[section]
            return DEFAULT_CONFIG[section][key]

    def update(self, section: str, key: str, value: Any) -> None:
        """Update a configuration value."""
        try:
            if section not in self.settings:
                self.settings[section] = {}
            self.settings[section][key] = value
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            logger.error(f"Error updating config: {e}")

# Global configuration instance
config = Config() 