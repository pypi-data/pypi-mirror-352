import pytest
from dotenv import load_dotenv

from airia import AiriaAsyncClient, AiriaClient

load_dotenv()


class TestAnthropicGateway:
    """Tests for the Anthropic gateway functionality."""

    def test_sync_anthropic_gateway_initialization(self):
        """Test initialization of the Anthropic gateway with sync client."""
        client = AiriaClient.with_anthropic_gateway()
        assert client.anthropic is not None
        assert client.anthropic.base_url == "https://gateway.airia.ai/anthropic/"

    def test_sync_anthropic_gateway_creation(self):
        """Test creating a simple message with the Anthropic gateway."""
        client = AiriaClient.with_anthropic_gateway()

        # Mock the Anthropic API call to avoid actual API calls during tests
        with pytest.MonkeyPatch().context() as m:
            # Simplified mock
            def mock_create(*args, **kwargs):
                class MockContent:
                    text = "Hello from Anthropic gateway"

                class MockResponse:
                    content = [MockContent()]

                return MockResponse()

            m.setattr(client.anthropic.messages, "create", mock_create)

            response = client.anthropic.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": "Hello"}],
            )

            assert response.content[0].text == "Hello from Anthropic gateway"


class TestAsyncAnthropicGateway:
    """Tests for the async Anthropic gateway functionality."""

    @pytest.mark.asyncio
    async def test_async_anthropic_gateway_initialization(self):
        """Test initialization of the Anthropic gateway with async client."""
        client = AiriaAsyncClient.with_anthropic_gateway()
        assert client.anthropic is not None
        assert client.anthropic.base_url == "https://gateway.airia.ai/anthropic/"

    @pytest.mark.asyncio
    async def test_async_anthropic_gateway_creation(self):
        """Test creating a simple message with the async Anthropic gateway."""
        client = AiriaAsyncClient.with_anthropic_gateway()

        # Mock the Anthropic API call to avoid actual API calls during tests
        with pytest.MonkeyPatch().context() as m:
            # Simplified mock
            async def mock_create(*args, **kwargs):
                class MockContent:
                    text = "Hello from async Anthropic gateway"

                class MockResponse:
                    content = [MockContent()]

                return MockResponse()

            m.setattr(client.anthropic.messages, "create", mock_create)

            response = await client.anthropic.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": "Hello"}],
            )

            assert response.content[0].text == "Hello from async Anthropic gateway"
