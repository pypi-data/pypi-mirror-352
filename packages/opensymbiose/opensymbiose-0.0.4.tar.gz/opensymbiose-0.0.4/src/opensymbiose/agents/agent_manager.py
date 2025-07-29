"""
AgentManager class to manage Mistral AI agents.
"""

import os
from typing import Dict, List, Optional

from mistralai import Mistral

from opensymbiose.agents.agent import Agent


class AgentManager:
    """
    Manages Mistral AI agents, including creation, retrieval, and handoffs.
    Implements the Singleton pattern to ensure only one instance exists.
    """

    _instance = None

    def __new__(cls, api_key: Optional[str] = None):
        """
        Create a new instance of AgentManager or return the existing one (Singleton pattern).

        Args:
            api_key: The Mistral API key. If not provided, it will be read from the environment.

        Returns:
            The AgentManager instance
        """
        if cls._instance is None:
            cls._instance = super(AgentManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AgentManager with the Mistral API key.

        Args:
            api_key: The Mistral API key. If not provided, it will be read from the environment.
        """
        # Skip initialization if already initialized (part of Singleton pattern)
        if self._initialized:
            return

        self.api_key = api_key or os.environ.get("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Mistral API key is required. Provide it as an argument or set the MISTRAL_API_KEY environment variable."
            )

        self.client = Mistral(self.api_key)
        self.agents: Dict[str, Agent] = {}
        self._initialized = True

    async def list_agents(self) -> List[Agent]:
        """
        List all agents from the Mistral API.

        Returns:
            A list of Agent objects
        """
        agent_list = await self.client.beta.agents.list_async()
        return [Agent(agent) for agent in agent_list]

    async def refresh_agents(self) -> None:
        """
        Refresh the local cache of agents from the Mistral API.
        """
        self.agents = {}
        agent_list = await self.client.beta.agents.list_async()
        for agent_data in agent_list:
            agent = Agent(agent_data)
            self.agents[agent.name] = agent

    async def get_agent(self, agent_name: str) -> Optional[Agent]:
        """
        Get an agent by name.

        Args:
            agent_name: The name of the agent

        Returns:
            The Agent object if found, None otherwise
        """
        # Refresh agents if not already loaded
        if not self.agents:
            await self.refresh_agents()

        return self.agents.get(agent_name)

    async def get_or_create_agent(
        self, agent_name: str, model: str, description: str, tools: List[Dict[str, str]]
    ) -> Agent:
        """
        Get an agent by name or create it if it doesn't exist.

        Args:
            agent_name: The name of the agent
            model: The model to use for the agent
            description: The description of the agent
            tools: The tools to enable for the agent

        Returns:
            The Agent object
        """
        # Refresh agents if not already loaded
        if not self.agents:
            await self.refresh_agents()

        # Check if agent exists
        agent = self.agents.get(agent_name)

        # Create agent if it doesn't exist
        if not agent:
            agent_data = await self.client.beta.agents.create_async(
                model=model, description=description, name=agent_name, tools=tools
            )
            agent = Agent(agent_data)
            self.agents[agent_name] = agent
            print(f"Created new agent: {agent}")
        else:
            print(f"Using existing agent: {agent}")

        return agent

    async def create_handoff(self, from_agent_name: str, to_agent_name: str) -> None:
        """
        Create a handoff from one agent to another.

        Args:
            from_agent_name: The name of the agent to handoff from
            to_agent_name: The name of the agent to handoff to
        """
        from_agent = await self.get_agent(from_agent_name)
        to_agent = await self.get_agent(to_agent_name)

        if not from_agent:
            raise ValueError(f"Agent '{from_agent_name}' not found")
        if not to_agent:
            raise ValueError(f"Agent '{to_agent_name}' not found")

        await from_agent.add_handoff(to_agent.id, self.client)

        # Update the local cache
        self.agents[from_agent_name] = from_agent
