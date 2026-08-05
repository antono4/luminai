"""OpenHands Cloud Client for LuminAI."""

import os
from dataclasses import dataclass
from typing import Any


@dataclass
class OpenHandsConfig:
    """Configuration for OpenHands Cloud."""

    api_key: str = ""
    base_url: str = "https://app.all-hands.dev"
    repository: str = "antono4/luminai"
    branch: str = "main"
    title_prefix: str = "[LuminAI]"


class OpenHandsClient:
    """Client for OpenHands Cloud API."""

    def __init__(self, config: OpenHandsConfig | None = None):
        self.config = config or OpenHandsConfig()
        
        if not self.config.api_key:
            self.config.api_key = os.environ.get("OPENHANDS_CLOUD_API_KEY", "")

    def _get_headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

    def start_conversation(
        self,
        message: str,
        title: str | None = None,
    ) -> dict[str, Any] | None:
        """Start a new OpenHands Cloud conversation."""
        import requests

        if not self.config.api_key:
            print("Error: OPENHANDS_CLOUD_API_KEY not set")
            return None

        url = f"{self.config.base_url}/api/v1/app-conversations"

        payload: dict[str, Any] = {
            "initial_message": {
                "content": [{"type": "text", "text": message}]
            },
        }

        if self.config.repository:
            payload["selected_repository"] = self.config.repository

        if self.config.branch:
            payload["selected_branch"] = self.config.branch

        if title:
            payload["title"] = title

        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()
            return data

        except requests.exceptions.RequestException as e:
            print(f"Failed to start conversation: {e}")
            return None

    def run_self_healing_task(
        self,
        task_description: str,
    ) -> dict[str, Any]:
        """Run a self-healing task on OpenHands Cloud."""
        title = f"{self.config.title_prefix} Self-Healing"

        conversation = self.start_conversation(
            message=task_description,
            title=title,
        )

        if not conversation:
            return {
                "success": False,
                "error": "Failed to start conversation",
            }

        return {
            "success": True,
            "conversation_id": conversation.get("app_conversation_id"),
            "conversation_url": f"{self.config.base_url}/conversations/{conversation.get('app_conversation_id')}",
            "status": conversation.get("execution_status"),
        }


def generate_task_message(stats: dict[str, Any]) -> str:
    """Generate task description for OpenHands."""
    return f"""# LuminAI Self-Healing Task

## Current Statistics
- Bugs Detected: {stats.get('bugs_detected', 0)}
- Bugs Fixed: {stats.get('bugs_fixed', 0)}
- Success Rate: {stats.get('success_rate', 0)}%
- Total Runs: {stats.get('total_runs', 0)}

## Tasks
1. Scan codebase for potential bugs
2. Analyze root cause
3. Implement fixes
4. Run tests to verify
5. Update documentation

Please execute the self-healing workflow for LuminAI (Perplexity API wrapper).
"""
