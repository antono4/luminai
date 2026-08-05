"""Configuration loader for LuminAI Self-Healing Agent."""

import os
from pathlib import Path
from typing import Any

import yaml


class Config:
    """Configuration manager for LuminAI Self-Healing Agent."""

    def __init__(self, config_path: str | Path | None = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "c4.yml"
        
        self.config_path = Path(config_path)
        self._config: dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                self._config = yaml.safe_load(f) or {}
        else:
            self._config = self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """Return default configuration."""
        return {
            "self_healing": {
                "enabled": True,
                "auto_fix": True,
                "max_retries": 3,
                "interval_minutes": 10,
            },
            "monitoring": {"enabled": True},
            "security": {
                "code_review_required": False,
                "max_fix_size": 200,
                "blocked_patterns": ["eval(", "exec(", "os.system"],
                "allowed_file_extensions": [".py"],
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value

    @property
    def is_enabled(self) -> bool:
        """Check if self-healing is enabled."""
        return self.get("self_healing.enabled", True)

    @property
    def is_auto_fix(self) -> bool:
        """Check if auto-fix is enabled."""
        return self.get("self_healing.auto_fix", True)

    @property
    def max_retries(self) -> int:
        """Get maximum retry count."""
        return self.get("self_healing.max_retries", 3)

    @property
    def interval_minutes(self) -> int:
        """Get interval in minutes."""
        return self.get("self_healing.interval_minutes", 10)


_config: Config | None = None


def get_config(config_path: str | Path | None = None) -> Config:
    """Get or create config instance."""
    global _config
    if _config is None or config_path is not None:
        _config = Config(config_path)
    return _config
