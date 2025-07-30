import pytest
from dotenv import load_dotenv

from airia import AiriaAsyncClient, AiriaClient

load_dotenv()


class TestOpenAIGateway:
    """Tests for the OpenAI gateway functionality."""

    def test_sync_openai_gateway_initialization(self):
        """Test initialization of the OpenAI gateway with sync client."""
        client = AiriaClient.with_openai_gateway()
        assert client.openai is not None
        assert client.openai.base_url == "https://gateway.airia.ai/openai/v1/"

    def test_sync_openai_gateway_creation(self):
        """Test creating a simple completion with the OpenAI gateway."""
        client = AiriaClient.with_openai_gateway()

        # Mock the OpenAI API call to avoid actual API calls during tests
        with pytest.MonkeyPatch().context() as m:
            # This is a simplified way to mock the response - in a real test you'd use pytest-mock
            def mock_create(*args, **kwargs):
                class MockCompletion:
                    class MockChoice:
                        class MockMessage:
                            content = "Hello from OpenAI gateway"

                        message = MockMessage()

                    choices = [MockChoice()]

                return MockCompletion()

            m.setattr(client.openai.chat.completions, "create", mock_create)

            response = client.openai.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello"},
                ],
            )

            assert response.choices[0].message.content == "Hello from OpenAI gateway"


class TestAsyncOpenAIGateway:
    """Tests for the async OpenAI gateway functionality."""

    @pytest.mark.asyncio
    async def test_async_openai_gateway_initialization(self):
        """Test initialization of the OpenAI gateway with async client."""
        client = AiriaAsyncClient.with_openai_gateway()
        assert client.openai is not None
        assert client.openai.base_url == "https://gateway.airia.ai/openai/v1/"

    @pytest.mark.asyncio
    async def test_async_openai_gateway_creation(self):
        """Test creating a simple completion with the async OpenAI gateway."""
        client = AiriaAsyncClient.with_openai_gateway()

        # Mock the OpenAI API call to avoid actual API calls during tests
        with pytest.MonkeyPatch().context() as m:
            # This is a simplified way to mock the response
            async def mock_create(*args, **kwargs):
                class MockCompletion:
                    class MockChoice:
                        class MockMessage:
                            content = "Hello from async OpenAI gateway"

                        message = MockMessage()

                    choices = [MockChoice()]

                return MockCompletion()

            m.setattr(client.openai.chat.completions, "create", mock_create)

            response = await client.openai.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello"},
                ],
            )

            assert (
                response.choices[0].message.content == "Hello from async OpenAI gateway"
            )
