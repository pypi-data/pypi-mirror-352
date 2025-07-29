"""
Module for creating and managing Mistral AI agents.
This module provides a simple interface to create and manage agents using the AgentManager class.
"""

from opensymbiose.agents.agent_manager import AgentManager


async def setup_agents():
    """
    Set up the agents for the application.

    Returns:
        A dictionary of agent names to Agent objects
    """
    # Initialize the agent manager (Singleton pattern ensures only one instance)
    agent_manager = AgentManager()

    # Get or create the test agent with web search tool
    test_agent = await agent_manager.get_or_create_agent(
        agent_name="Test Agent Tools",
        model="mistral-medium-latest",
        description="An agent with tools",
        tools=[{"type": "web_search"}],
    )

    # Get or create the calculating agent with code interpreter tool
    calculating_agent = await agent_manager.get_or_create_agent(
        agent_name="Calculating Agent",
        model="mistral-medium-latest",
        description="A calculating agent with tools",
        tools=[{"type": "code_interpreter"}],
    )

    # Create handoff from test agent to calculating agent
    await agent_manager.create_handoff("Test Agent Tools", "Calculating Agent")

    # Return a dictionary of agent names to Agent objects
    return {"test_agent_tools": test_agent, "calculating_agent": calculating_agent}


# Create a convenience function to get the agents
async def get_agents():
    """
    Get the agents for the application.

    Returns:
        A dictionary of agent names to Agent objects
    """
    return await setup_agents()


# For backwards compatibility and direct script execution
# Note: This is now just a placeholder as setup_agents() is async and can't be awaited at module level
symbiose_agents = {}
