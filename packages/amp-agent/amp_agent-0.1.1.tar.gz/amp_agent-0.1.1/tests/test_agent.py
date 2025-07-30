import pytest
from amp_agent.agent_interface import AgentInterface


class TestAgent(AgentInterface):
    async def process_message(self, content: str, metadata: dict = None) -> str:
        return f"Test: {content}"


@pytest.fixture
def test_agent():
    return TestAgent()


@pytest.mark.asyncio
async def test_process_message(test_agent):
    content = "Hello, World!"
    result = await test_agent.process_message(content)
    assert result == "Test: Hello, World!"


@pytest.mark.asyncio
async def test_process_message_with_metadata(test_agent):
    content = "Hello, World!"
    metadata = {"key": "value"}
    result = await test_agent.process_message(content, metadata)
    assert result == "Test: Hello, World!" 