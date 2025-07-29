"""
Agent class to represent individual Mistral AI agents.
"""

from typing import Any

from mistralai import Mistral


class Agent:
    """
    Represents a Mistral AI agent with its properties and capabilities.
    """

    def __init__(self, agent_data: Any):
        """
        Initialize an Agent object from Mistral API agent data.

        Args:
            agent_data: The agent data returned from Mistral API
        """
        self.id = agent_data.id
        self.name = agent_data.name
        self.description = agent_data.description
        self.model = agent_data.model
        self.tools = agent_data.tools
        self.handoffs = agent_data.handoffs if hasattr(agent_data, "handoffs") else []
        self._raw_data = agent_data

    @property
    def raw_data(self) -> Any:
        """
        Get the raw agent data from Mistral API.

        Returns:
            The raw agent data
        """
        return self._raw_data

    async def add_handoff(self, agent_id: str, client: Mistral) -> None:
        """
        Add a handoff to another agent.

        Args:
            agent_id: The ID of the agent to handoff to
            client: The Mistral client instance
        """
        if agent_id not in self.handoffs:
            self.handoffs.append(agent_id)
            updated_agent = await client.beta.agents.update_async(
                agent_id=self.id, handoffs=self.handoffs
            )
            # Update the raw data with the updated agent
            self._raw_data = updated_agent

    async def remove_handoff(self, agent_id: str, client: Mistral) -> None:
        """
        Remove a handoff to another agent.

        Args:
            agent_id: The ID of the agent to remove handoff from
            client: The Mistral client instance
        """
        if agent_id in self.handoffs:
            self.handoffs.remove(agent_id)
            updated_agent = await client.beta.agents.update_async(
                agent_id=self.id, handoffs=self.handoffs
            )
            # Update the raw data with the updated agent
            self._raw_data = updated_agent

    def __str__(self) -> str:
        """
        String representation of the agent.

        Returns:
            A string representation of the agent
        """
        return f"Agent(id={self.id}, name={self.name}, model={self.model})"

    def __repr__(self) -> str:
        """
        Detailed representation of the agent.

        Returns:
            A detailed representation of the agent
        """
        return (
            f"Agent(id={self.id}, name={self.name}, "
            f"description={self.description}, model={self.model}, "
            f"tools={self.tools}, handoffs={self.handoffs})"
        )
