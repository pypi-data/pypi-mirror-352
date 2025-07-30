"""Agent-specific API operations."""

from typing import Any, Optional

from ..http import HTTPClient

AGENT_TYPE = "sdk_v0"


class AgentAPI:
    """Agent management API endpoints."""

    def __init__(self, http: HTTPClient):
        self.http = http

    def list(self) -> dict[str, Any]:
        """Get all agents."""
        return self.http.get("agents")

    def get(self, username: str) -> dict[str, Any]:
        """Get agent details by username."""
        return self.http.get(f"agents/{username}")

    def create(
        self,
        username: str,
        name: str,
        description: Optional[str] = None,
        url: Optional[str] = None,
        visibility: str = "private",
    ) -> dict[str, Any]:
        """Create a new agent."""
        # required
        data = {
            "username": username,
            "name": name,
            "visibility": visibility,
            "agentConfig": {"url": url},
            "agentType": AGENT_TYPE,
        }
        # optional
        if description is not None:
            data["description"] = description

        return self.http.post("agents", data)

    def update(
        self,
        username: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        url: Optional[str] = None,
        visibility: str = "private",
    ) -> dict[str, Any]:
        """Create a new agent."""
        # required
        data = {
            "username": username,
            "name": name,
            "visibility": visibility,
            "agentConfig": {"url": url},
            "agentType": AGENT_TYPE,
        }
        # optional
        if description is not None:
            data["description"] = description

        return self.http.put(f"agents/{username}", data)

    def delete(self, username: str) -> dict[str, Any]:
        """Delete an agent."""
        return self.http.delete(f"agents/{username}")
