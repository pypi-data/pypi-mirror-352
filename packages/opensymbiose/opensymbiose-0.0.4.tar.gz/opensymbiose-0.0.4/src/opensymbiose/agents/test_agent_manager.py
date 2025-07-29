"""
Test script for the AgentManager and Agent classes.
"""

import asyncio
import os
import sys

# Add the parent directory to the path to allow importing the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from opensymbiose.agents.agent_manager import AgentManager
from opensymbiose.agents.create_agents import setup_agents, get_agents


def test_agent_manager():
    """
    Test the AgentManager class.
    """
    print("Testing AgentManager...")

    # Test singleton pattern
    manager1 = AgentManager()
    manager2 = AgentManager()
    assert manager1 is manager2, "Singleton pattern failed"
    print("✓ Singleton pattern works")

    # Test listing agents
    agents = manager1.list_agents()
    print(f"Found {len(agents)} agents")

    # Test refreshing agents
    manager1.refresh_agents()
    print(f"Refreshed agents, found {len(manager1.agents)} agents")

    # Test getting an agent
    if manager1.agents:
        agent_name = list(manager1.agents.keys())[0]
        agent = manager1.get_agent(agent_name)
        print(f"Got agent: {agent}")

    print("AgentManager tests completed successfully")


async def test_create_agents():
    """
    Test the create_agents module.
    """
    print("\nTesting create_agents module...")

    # Test setup_agents function
    agents = await setup_agents()
    assert "test_agent_tools" in agents, "Test agent not created"
    assert "calculating_agent" in agents, "Calculating agent not created"

    print(f"✓ setup_agents created {len(agents)} agents")

    # Test get_agents function
    agents2 = await get_agents()
    assert agents2["test_agent_tools"].id == agents["test_agent_tools"].id, (
        "get_agents returned different agents"
    )

    print("✓ get_agents works correctly")

    # Test handoffs
    test_agent = agents["test_agent_tools"]
    calc_agent = agents["calculating_agent"]

    assert calc_agent.id in test_agent.handoffs, "Handoff not created"

    print(f"✓ Handoff from {test_agent.name} to {calc_agent.name} created successfully")

    print("create_agents tests completed successfully")


async def main():
    """Run all tests."""
    # Check if MISTRAL_API_KEY is set
    if not os.environ.get("MISTRAL_API_KEY"):
        print("Error: MISTRAL_API_KEY environment variable is not set")
        print("Please set it before running this test script")
        sys.exit(1)

    test_agent_manager()
    await test_create_agents()

    print("\nAll tests completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
