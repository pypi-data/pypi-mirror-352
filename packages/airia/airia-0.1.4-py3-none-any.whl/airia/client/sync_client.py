from typing import Any, Dict, List, Literal, Optional, overload
from urllib.parse import urljoin

import loguru
import requests

from ..exceptions import AiriaAPIError
from ..types import (
    ApiVersion,
    PipelineExecutionDebugResponse,
    PipelineExecutionResponse,
    PipelineExecutionV1StreamedResponse,
    PipelineExecutionV2StreamedResponse,
    RequestData,
)
from .base_client import AiriaBaseClient


class AiriaClient(AiriaBaseClient):
    """Synchronous client for interacting with the Airia API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        log_requests: bool = False,
        custom_logger: Optional["loguru.Logger"] = None,
    ):
        """
        Initialize the synchronous Airia API client.

        Args:
            api_key: API key for authentication. If not provided, will attempt to use AIRIA_API_KEY environment variable.
            timeout: Request timeout in seconds.
            log_requests: Whether to log API requests and responses. Default is False.
            custom_logger: Optional custom logger object to use for logging. If not provided, will use a default logger when `log_requests` is True.
        """
        super().__init__(api_key, timeout, log_requests, custom_logger)

        # Initialize session for synchronous requests
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    @classmethod
    def with_openai_gateway(
        cls,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        log_requests: bool = False,
        custom_logger: Optional["loguru.Logger"] = None,
        **kwargs,
    ):
        """
        Initialize the synchronous Airia API client with OpenAI gateway capabilities.

        Args:
            api_key: API key for authentication. If not provided, will attempt to use AIRIA_API_KEY environment variable.
            timeout: Request timeout in seconds.
            log_requests: Whether to log API requests and responses. Default is False.
            custom_logger: Optional custom logger object to use for logging. If not provided, will use a default logger when `log_requests` is True.
            **kwargs: Additional keyword arguments to pass to the OpenAI client initialization.
        """
        from openai import OpenAI

        api_key = cls._get_api_key(api_key)
        cls.openai = OpenAI(
            api_key=api_key,
            base_url="https://gateway.airia.ai/openai/v1",
            **kwargs,
        )

        return cls(api_key, timeout, log_requests, custom_logger)

    @classmethod
    def with_anthropic_gateway(
        cls,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        log_requests: bool = False,
        custom_logger: Optional["loguru.Logger"] = None,
        **kwargs,
    ):
        """
        Initialize the synchronous Airia API client with Anthropic gateway capabilities.

        Args:
            api_key: API key for authentication. If not provided, will attempt to use AIRIA_API_KEY environment variable.
            timeout: Request timeout in seconds.
            log_requests: Whether to log API requests and responses. Default is False.
            custom_logger: Optional custom logger object to use for logging. If not provided, will use a default logger when `log_requests` is True.
            **kwargs: Additional keyword arguments to pass to the Anthropic client initialization.
        """
        from anthropic import Anthropic

        api_key = cls._get_api_key(api_key)
        cls.anthropic = Anthropic(
            api_key=api_key,
            base_url="https://gateway.airia.ai/anthropic",
            **kwargs,
        )

        return cls(api_key, timeout, log_requests, custom_logger)

    def _handle_exception(self, e: requests.HTTPError, url: str, correlation_id: str):
        # Log the error response if enabled
        if self.log_requests:
            self.logger.error(
                f"API Error: {e.response.status_code} {e.response.reason}\n"
                f"URL: {url}\n"
                f"Correlation ID: {correlation_id}"
            )

        # Extract error details from response if possible
        error_message = "API request failed"
        try:
            error_data = e.response.json()
            if isinstance(error_data, dict) and "message" in error_data:
                error_message = error_data["message"]
            elif isinstance(error_data, dict) and "error" in error_data:
                error_message = error_data["error"]
        except (ValueError, KeyError):
            # If JSON parsing fails or expected keys are missing
            error_message = f"API request failed: {str(e)}"

        # Make sure API key is not included in error messages
        sanitized_message = (
            error_message.replace(self.api_key, "[REDACTED]")
            if self.api_key in error_message
            else error_message
        )

        # Raise custom exception with status code and sanitized message
        raise AiriaAPIError(
            status_code=e.response.status_code, message=sanitized_message
        ) from e

    def _make_request(self, method: str, request_data: RequestData):
        """
        Makes a synchronous HTTP request to the Airia API.

        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST')
            request_data: A dictionary containing the following request information:
                - url: The endpoint URL for the request
                - headers: HTTP headers to include in the request
                - payload: The JSON payload/body for the request
                - correlation_id: Unique identifier for request tracing

        Returns:
            resp (Dict[str, Any]): The JSON response from the API as a dictionary.

        Raises:
            AiriaAPIError: If the API returns an error response, with details about the error
            requests.HTTPError: For HTTP-related errors

        Note:
            This is an internal method used by other client methods to make API requests.
            It handles logging, error handling, and API key redaction in error messages.
        """
        try:
            # Make the request
            response = self.session.request(
                method=method,
                url=request_data.url,
                json=request_data.payload,
                headers=request_data.headers,
                timeout=self.timeout,
            )

            # Log the response if enabled
            if self.log_requests:
                self.logger.info(
                    f"API Response: {response.status_code} {response.reason}\n"
                    f"URL: {request_data.url}\n"
                    f"Correlation ID: {request_data.correlation_id}\n"
                )

            # Check for HTTP errors
            response.raise_for_status()

            # Returns the JSON response
            return response.json()

        except requests.HTTPError as e:
            self._handle_exception(e, request_data.url, request_data.correlation_id)

    def _make_request_stream(self, method: str, request_data: RequestData):
        """
        Makes a synchronous HTTP request to the Airia API.

        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST')
            request_data: A dictionary containing the following request information:
                - url: The endpoint URL for the request
                - headers: HTTP headers to include in the request
                - payload: The JSON payload/body for the request
                - correlation_id: Unique identifier for request tracing
            stream (bool): If True, the response will be streamed instead of downloaded all at once

        Yields:
            resp (Iterator[str]): Yields chunks of the response as they are received.

        Raises:
            AiriaAPIError: If the API returns an error response, with details about the error
            requests.HTTPError: For HTTP-related errors

        Note:
            This is an internal method used by other client methods to make API requests.
            It handles logging, error handling, and API key redaction in error messages.
        """
        try:
            # Make the request
            response = self.session.request(
                method=method,
                url=request_data.url,
                json=request_data.payload,
                headers=request_data.headers,
                timeout=self.timeout,
                stream=True,
            )

            # Log the response if enabled
            if self.log_requests:
                self.logger.info(
                    f"API Response: {response.status_code} {response.reason}\n"
                    f"URL: {request_data.url}\n"
                    f"Correlation ID: {request_data.correlation_id}\n"
                )

            # Check for HTTP errors
            response.raise_for_status()

            # Yields the response content as a stream
            for chunk in response.iter_content():
                yield chunk.decode("utf-8")

        except requests.HTTPError as e:
            self._handle_exception(e, request_data.url, request_data.correlation_id)

    @overload
    def execute_pipeline(
        self,
        pipeline_id: str,
        user_input: str,
        debug: Literal[False] = False,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        async_output: Literal[False] = False,
        include_tools_response: bool = False,
        images: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        data_source_folders: Optional[Dict[str, Any]] = None,
        data_source_files: Optional[Dict[str, Any]] = None,
        in_memory_messages: Optional[List[Dict[str, str]]] = None,
        current_date_time: Optional[str] = None,
        save_history: bool = True,
        additional_info: Optional[List[Any]] = None,
        prompt_variables: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V2.value,
    ) -> PipelineExecutionResponse: ...

    @overload
    def execute_pipeline(
        self,
        pipeline_id: str,
        user_input: str,
        debug: Literal[True] = True,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        async_output: Literal[False] = False,
        include_tools_response: bool = False,
        images: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        data_source_folders: Optional[Dict[str, Any]] = None,
        data_source_files: Optional[Dict[str, Any]] = None,
        in_memory_messages: Optional[List[Dict[str, str]]] = None,
        current_date_time: Optional[str] = None,
        save_history: bool = True,
        additional_info: Optional[List[Any]] = None,
        prompt_variables: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V2.value,
    ) -> PipelineExecutionDebugResponse: ...

    @overload
    def execute_pipeline(
        self,
        pipeline_id: str,
        user_input: str,
        debug: bool = False,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        async_output: Literal[True] = True,
        include_tools_response: bool = False,
        images: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        data_source_folders: Optional[Dict[str, Any]] = None,
        data_source_files: Optional[Dict[str, Any]] = None,
        in_memory_messages: Optional[List[Dict[str, str]]] = None,
        current_date_time: Optional[str] = None,
        save_history: bool = True,
        additional_info: Optional[List[Any]] = None,
        prompt_variables: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        api_version: Literal["v2"] = ApiVersion.V2.value,
    ) -> PipelineExecutionV2StreamedResponse: ...

    @overload
    def execute_pipeline(
        self,
        pipeline_id: str,
        user_input: str,
        debug: bool = False,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        async_output: Literal[True] = True,
        include_tools_response: bool = False,
        images: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        data_source_folders: Optional[Dict[str, Any]] = None,
        data_source_files: Optional[Dict[str, Any]] = None,
        in_memory_messages: Optional[List[Dict[str, str]]] = None,
        current_date_time: Optional[str] = None,
        save_history: bool = True,
        additional_info: Optional[List[Any]] = None,
        prompt_variables: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        api_version: Literal["v1"] = ApiVersion.V1.value,
    ) -> PipelineExecutionV1StreamedResponse: ...

    def execute_pipeline(
        self,
        pipeline_id: str,
        user_input: str,
        debug: bool = False,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        async_output: bool = False,
        include_tools_response: bool = False,
        images: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        data_source_folders: Optional[Dict[str, Any]] = None,
        data_source_files: Optional[Dict[str, Any]] = None,
        in_memory_messages: Optional[List[Dict[str, str]]] = None,
        current_date_time: Optional[str] = None,
        save_history: bool = True,
        additional_info: Optional[List[Any]] = None,
        prompt_variables: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V2.value,
    ):
        """
        Execute a pipeline with the provided input.

        Args:
            pipeline_id: The ID of the pipeline to execute.
            user_input: input text to process.
            debug: Whether debug mode execution is enabled. Default is False.
            user_id: Optional ID of the user making the request (guid).
            conversation_id: Optional conversation ID (guid).
            async_output: Whether to stream the response. Default is False.
            include_tools_response: Whether to return the initial LLM tool result. Default is False.
            images: Optional list of images formatted as base64 strings.
            files: Optional list of files formatted as base64 strings.
            data_source_folders: Optional data source folders information.
            data_source_files: Optional data source files information.
            in_memory_messages: Optional list of in-memory messages, each with a role and message.
            current_date_time: Optional current date and time in ISO format.
            save_history: Whether to save the userInput and output to conversation history. Default is True.
            additional_info: Optional additional information.
            prompt_variables: Optional variables to be used in the prompt.
            correlation_id: Optional correlation ID for request tracing. If not provided,
                        one will be generated automatically.
            api_version: API version to use. Default is `v2`

        Returns:
            The API response as a dictionary.

        Raises:
            AiriaAPIError: If the API request fails with details about the error.
            requests.RequestException: For other request-related errors.

        Example:
            >>> client = AiriaClient(api_key="your_api_key")
            >>> response = client.execute_pipeline(
            ...     pipeline_id="pipeline_123",
            ...     user_input="Tell me about quantum computing"
            ... )
            >>> print(response.result)
        """
        request_data = self._pre_execute_pipeline(
            pipeline_id=pipeline_id,
            user_input=user_input,
            debug=debug,
            user_id=user_id,
            conversation_id=conversation_id,
            async_output=async_output,
            include_tools_response=include_tools_response,
            images=images,
            files=files,
            data_source_folders=data_source_folders,
            data_source_files=data_source_files,
            in_memory_messages=in_memory_messages,
            current_date_time=current_date_time,
            save_history=save_history,
            additional_info=additional_info,
            prompt_variables=prompt_variables,
            correlation_id=correlation_id,
            api_version=api_version,
        )
        stream = async_output and api_version == ApiVersion.V2.value
        if stream:
            resp = self._make_request_stream("POST", request_data)
        else:
            resp = self._make_request("POST", request_data)

        if not async_output:
            if not debug:
                return PipelineExecutionResponse(**resp)
            return PipelineExecutionDebugResponse(**resp)

        if api_version == ApiVersion.V1.value:
            url = urljoin(
                self.base_url, f"{api_version}/StreamSocketConfig/GenerateUrl"
            )
            request_data = self._prepare_request(
                url,
                {"socketIdentifier": resp},
                request_data.headers["X-Correlation-ID"],
            )
            resp = self._make_request("POST", request_data)

            return PipelineExecutionV1StreamedResponse(**resp)

        return PipelineExecutionV2StreamedResponse(stream=resp)
