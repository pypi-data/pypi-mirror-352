import json

import pytest
from dotenv import load_dotenv

from airia import AiriaAsyncClient, AiriaClient

load_dotenv()
PYTHON_PIPELINE = "0134da17-c5a5-4730-a576-92f8eaf0926f"
GPT_4O_MINI_PIPELINE = "367969f1-7a11-40f0-bab6-c8f901fdb537"
USER_INPUT = "test"


# Fixtures for the sync client
@pytest.fixture
def sync_client():
    """Create a sync client with test API key."""
    return AiriaClient(log_requests=True)


# Fixtures for the async client
@pytest.fixture
def async_client():
    """Create an async client with test API key."""
    return AiriaAsyncClient(log_requests=True)


class TestSyncPipelineExecution:
    """Tests for synchronous execute_pipeline method."""

    def test_execute_pipeline_minimal(self, sync_client: AiriaClient):
        """Test execute_pipeline with only pipeline_id."""
        expected_response = {
            "result": USER_INPUT,
            "report": None,
            "isBackupPipeline": False,
        }
        response = sync_client.execute_pipeline(
            pipeline_id=PYTHON_PIPELINE, user_input=USER_INPUT
        )
        assert response.model_dump() == expected_response

    def test_execute_pipeline_with_debug(self, sync_client: AiriaClient):
        """Test execute_pipeline with debug parameter."""
        response = sync_client.execute_pipeline(
            pipeline_id=PYTHON_PIPELINE, user_input=USER_INPUT, debug=True
        )
        assert response.report is not None

    def test_execute_pipeline_with_async_output_v1(self, sync_client: AiriaClient):
        """Test execute_pipeline with async_output parameter."""
        response = sync_client.execute_pipeline(
            pipeline_id=PYTHON_PIPELINE,
            user_input=USER_INPUT,
            async_output=True,
            api_version="v1",
        )
        assert hasattr(response, "webSocketUrl")

    def test_execute_pipeline_with_async_output_v2(self, sync_client: AiriaClient):
        """Test execute_pipeline with async_output parameter."""
        response = sync_client.execute_pipeline(
            pipeline_id=PYTHON_PIPELINE, user_input=USER_INPUT, async_output=True
        )
        assert hasattr(response, "stream")

    def test_execute_pipeline_with_include_tools_response(
        self, sync_client: AiriaClient
    ):
        """Test execute_pipeline with include_tools_response parameter."""
        response = sync_client.execute_pipeline(
            pipeline_id=GPT_4O_MINI_PIPELINE,
            user_input="2+2",
            include_tools_response=True,
        )
        calculator_tool = json.loads(response.result.split("```")[1].split("```")[0])

        assert isinstance(calculator_tool, dict)

    def test_execute_pipeline_with_images(self, sync_client: AiriaClient):
        """Test execute_pipeline with images parameter."""
        with open("tests/assets/test_image.txt") as f:
            image_data = f.read()
        response = sync_client.execute_pipeline(
            pipeline_id=PYTHON_PIPELINE, user_input=USER_INPUT, images=[image_data]
        )

        assert response.result == "1 images"

    def test_execute_pipeline_with_files(self, sync_client: AiriaClient):
        """Test execute_pipeline with files parameter."""
        with open("tests/assets/test_pdf.txt") as f:
            pdf_data = f.read()
        response = sync_client.execute_pipeline(
            pipeline_id=PYTHON_PIPELINE, user_input=USER_INPUT, files=[pdf_data]
        )

        assert response.result == "1 files"

    def test_execute_pipeline_with_in_memory_messages(self, sync_client: AiriaClient):
        """Test execute_pipeline with in_memory_messages parameter."""
        in_memory_messages = [
            {"role": "user", "message": "always respond with 'Airia'"}
        ]
        response = sync_client.execute_pipeline(
            pipeline_id=GPT_4O_MINI_PIPELINE,
            user_input=USER_INPUT,
            in_memory_messages=in_memory_messages,
        )

        assert response.result == "Airia"

    def test_execute_pipeline_with_additional_info(self, sync_client: AiriaClient):
        """Test execute_pipeline with additional_info parameter."""
        additional_info = ["additional_info"]
        response = sync_client.execute_pipeline(
            pipeline_id=PYTHON_PIPELINE,
            user_input=USER_INPUT,
            additional_info=additional_info,
        )

        assert response.result == str(additional_info)


class TestAsyncPipelineExecution:
    """Tests for asynchronous execute_pipeline method."""

    @pytest.mark.asyncio
    async def test_execute_pipeline_minimal(self, async_client: AiriaAsyncClient):
        """Test execute_pipeline with only pipeline_id."""
        expected_response = {
            "result": USER_INPUT,
            "report": None,
            "isBackupPipeline": False,
        }
        async with async_client:
            response = await async_client.execute_pipeline(
                pipeline_id=PYTHON_PIPELINE, user_input=USER_INPUT
            )
        assert response.model_dump() == expected_response

    @pytest.mark.asyncio
    async def test_execute_pipeline_with_debug(self, async_client: AiriaAsyncClient):
        """Test execute_pipeline with debug parameter."""
        async with async_client:
            response = await async_client.execute_pipeline(
                pipeline_id=PYTHON_PIPELINE, user_input=USER_INPUT, debug=True
            )
        assert response.report is not None

    @pytest.mark.asyncio
    async def test_execute_pipeline_with_async_output(
        self, async_client: AiriaAsyncClient
    ):
        """Test execute_pipeline with async_output parameter."""
        async with async_client:
            response = await async_client.execute_pipeline(
                pipeline_id=PYTHON_PIPELINE, user_input=USER_INPUT, async_output=True, api_version="v1"
            )
            assert hasattr(response, "webSocketUrl")


    @pytest.mark.asyncio
    async def test_execute_pipeline_with_async_output_v2(
        self, async_client: AiriaAsyncClient
    ):
        """Test execute_pipeline with async_output parameter."""
        async with async_client:
            response = await async_client.execute_pipeline(
                pipeline_id=PYTHON_PIPELINE, user_input=USER_INPUT, async_output=True
            )
            assert hasattr(response, "stream")


    @pytest.mark.asyncio
    async def test_execute_pipeline_with_include_tools_response(
        self, async_client: AiriaAsyncClient
    ):
        """Test execute_pipeline with include_tools_response parameter."""
        async with async_client:
            response = await async_client.execute_pipeline(
                pipeline_id=GPT_4O_MINI_PIPELINE,
                user_input="2+2",
                include_tools_response=True,
            )
        calculator_tool = json.loads(response.result.split("```")[1].split("```")[0])

        assert isinstance(calculator_tool, dict)

    @pytest.mark.asyncio
    async def test_execute_pipeline_with_images(self, async_client: AiriaAsyncClient):
        """Test execute_pipeline with images parameter."""
        with open("tests/assets/test_image.txt") as f:
            image_data = f.read()

        async with async_client:
            response = await async_client.execute_pipeline(
                pipeline_id=PYTHON_PIPELINE, user_input=USER_INPUT, images=[image_data]
            )

        assert response.result == "1 images"

    @pytest.mark.asyncio
    async def test_execute_pipeline_with_files(self, async_client: AiriaAsyncClient):
        """Test execute_pipeline with files parameter."""
        with open("tests/assets/test_pdf.txt") as f:
            pdf_data = f.read()

        async with async_client:
            response = await async_client.execute_pipeline(
                pipeline_id=PYTHON_PIPELINE, user_input=USER_INPUT, files=[pdf_data]
            )

        assert response.result == "1 files"

    @pytest.mark.asyncio
    async def test_execute_pipeline_with_in_memory_messages(
        self, async_client: AiriaAsyncClient
    ):
        """Test execute_pipeline with in_memory_messages parameter."""
        in_memory_messages = [
            {"role": "user", "message": "always respond with 'Airia'"}
        ]

        async with async_client:
            response = await async_client.execute_pipeline(
                pipeline_id=GPT_4O_MINI_PIPELINE,
                user_input=USER_INPUT,
                in_memory_messages=in_memory_messages,
            )

        assert response.result == "Airia"

    @pytest.mark.asyncio
    async def test_execute_pipeline_with_additional_info(
        self, async_client: AiriaAsyncClient
    ):
        """Test execute_pipeline with additional_info parameter."""
        additional_info = ["additional_info"]

        async with async_client:
            response = await async_client.execute_pipeline(
                pipeline_id=PYTHON_PIPELINE,
                user_input=USER_INPUT,
                additional_info=additional_info,
            )

        assert response.result == str(additional_info)
