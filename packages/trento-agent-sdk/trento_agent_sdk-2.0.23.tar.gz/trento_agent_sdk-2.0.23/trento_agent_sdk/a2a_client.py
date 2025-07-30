import uuid
import aiohttp
import asyncio
import logging
from typing import Optional, Union

from .a2a.models.AgentCard import AgentCard, AgentSkill
from .a2a.models.Task import Message, TextPart
from .a2a.models.Types import (
    SendTaskResponse,
    GetTaskResponse,
    CancelTaskResponse,
)

logger = logging.getLogger(__name__)


class A2AClient:
    """
    Client for interacting with A2A (Agent-to-Agent) servers.

    This client provides methods to:
    - Fetch agent capabilities (agent card)
    - Send tasks to agents
    - Get task status and results
    - Cancel tasks
    """

    def __init__(self, server_url: str):
        """
        Initialize the A2A client.

        Args:
            server_url: The base URL of the A2A server (e.g., "http://localhost:8000")
        """
        self.server_url = server_url.rstrip("/")
        self.session = None

    async def __aenter__(self):
        """Set up the aiohttp session when used as an async context manager."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close the aiohttp session when exiting the async context manager."""
        if self.session:
            await self.session.close()
            self.session = None

    async def _ensure_session(self):
        """Ensure that an aiohttp session exists."""
        if self.session is None:
            # Configure connection pooling for better performance
            connector = aiohttp.TCPConnector(
                limit=10,  # Maximum number of connections
                ttl_dns_cache=300,  # DNS cache TTL in seconds
                use_dns_cache=True,
                ssl=False  # Set to appropriate SSL context if needed
            )
            self.session = aiohttp.ClientSession(connector=connector)

    async def close(self):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None

    async def get_agent_card(self, max_retries: int = 3, retry_delay: float = 1.0) -> AgentCard:
        """
        Fetch the agent card from the A2A server with retry mechanism.

        Args:
            max_retries: Maximum number of retry attempts (default: 3)
            retry_delay: Delay between retry attempts in seconds (default: 1.0)

        Returns:
            AgentCard: The agent's capabilities and metadata.

        Raises:
            Exception: If all request attempts fail or return invalid responses.
        """
        await self._ensure_session()

        last_exception = None
        for attempt in range(max_retries):
            try:
                async with self.session.get(
                    f"{self.server_url}/.well-known/agent.json",
                    timeout=aiohttp.ClientTimeout(total=10)  # 10 seconds timeout
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        error_msg = f"Failed to get agent card: {response.status} - {error_text}"
                        if attempt < max_retries - 1:
                            logger.warning(f"{error_msg}. Retrying ({attempt+1}/{max_retries})...")
                            await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                            continue
                        raise Exception(error_msg)

                    data = await response.json()

                    # Convert from server format to AgentCard format
                    if "skills" in data and data["skills"]:
                        skills = [AgentSkill(**skill) for skill in data["skills"]]
                    else:
                        skills = None

                    return AgentCard(
                        name=data.get("name", ""),
                        description=data.get("description", ""),
                        url=data.get("url", ""),
                        version=data.get("version", ""),
                        skills=skills,
                        default_input_modes=data.get("defaultInputModes", ["text/plain"]),
                        default_output_modes=data.get("defaultOutputModes", ["text/plain"]),
                        provider=data.get("provider"),
                        documentation_url=data.get("documentationUrl"),
                    )
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_exception = e
                if attempt < max_retries - 1:
                    logger.warning(f"Connection error: {str(e)}. Retrying ({attempt+1}/{max_retries})...")
                    await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
            except Exception as e:
                raise Exception(f"Error fetching agent card: {str(e)}")

        # If we've reached here, all retries failed
        raise Exception(f"Failed to fetch agent card after {max_retries} attempts: {str(last_exception)}")

    async def send_task(
        self,
        message: Union[str, Message],
        task_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> SendTaskResponse:
        """
        Send a task to the A2A server.

        Args:
            message: The message to send to the agent. Can be a string or a Message object.
            task_id: Optional task ID. If not provided, a UUID will be generated.
            session_id: Optional session ID for related tasks.

        Returns:
            SendTaskResponse: The response from the server containing the task information.

        Raises:
            Exception: If the request fails or returns an invalid response.
        """
        await self._ensure_session()

        # Generate a task ID if not provided
        if task_id is None:
            task_id = str(uuid.uuid4())

        # Generate a session ID if not provided
        if session_id is None:
            session_id = str(uuid.uuid4())

        # Convert string message to Message object with TextPart if needed
        if isinstance(message, str):
            # Ensure message text is never None
            safe_message = message if message is not None else ""
            message = Message(
                role="user", parts=[TextPart(type="text", text=safe_message)]
            )
        # If it's already a Message object, ensure its parts have valid text
        elif hasattr(message, "parts") and message.parts:
            sanitized_parts = []
            for part in message.parts:
                if hasattr(part, "type") and part.type == "text":
                    # Create a properly sanitized TextPart with empty string instead of None
                    if not hasattr(part, "text") or part.text is None:
                        sanitized_parts.append(TextPart(type="text", text=""))
                    else:
                        sanitized_parts.append(TextPart(type="text", text=part.text))
                else:
                    # For non-TextPart types, just add them as is
                    sanitized_parts.append(part)
            message.parts = sanitized_parts

        # Create the request payload
        payload = {
            "id": str(uuid.uuid4()),  # Request ID
            "params": {
                "id": task_id,
                "sessionId": session_id,
                "message": (
                    message.dict(exclude_none=True)
                    if hasattr(message, "dict")
                    else message
                ),
            },
        }

        try:
            async with self.session.post(
                f"{self.server_url}/tasks/send", json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(
                        f"Failed to send task: {response.status} - {error_text}"
                    )

                data = await response.json()
                return SendTaskResponse(**data)
        except Exception as e:
            raise Exception(f"Error sending task: {str(e)}")

    async def get_task(self, task_id: str) -> GetTaskResponse:
        """
        Get the status and result of a task.

        Args:
            task_id: The ID of the task to retrieve.

        Returns:
            GetTaskResponse: The response from the server containing the task status and result.

        Raises:
            Exception: If the request fails or returns an invalid response.
        """
        await self._ensure_session()

        # Create the request payload
        payload = {"id": str(uuid.uuid4()), "params": {"id": task_id}}  # Request ID

        try:
            async with self.session.post(
                f"{self.server_url}/tasks/get", json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(
                        f"Failed to get task: {response.status} - {error_text}"
                    )

                data = await response.json()
                return GetTaskResponse(**data)
        except Exception as e:
            raise Exception(f"Error getting task: {str(e)}")

    async def cancel_task(self, task_id: str) -> CancelTaskResponse:
        """
        Cancel a task.

        Args:
            task_id: The ID of the task to cancel.

        Returns:
            CancelTaskResponse: The response from the server confirming the cancellation.

        Raises:
            Exception: If the request fails or returns an invalid response.
        """
        await self._ensure_session()

        # Create the request payload
        payload = {"id": str(uuid.uuid4()), "params": {"id": task_id}}  # Request ID

        try:
            async with self.session.post(
                f"{self.server_url}/tasks/cancel", json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(
                        f"Failed to cancel task: {response.status} - {error_text}"
                    )

                data = await response.json()
                return CancelTaskResponse(**data)
        except Exception as e:
            raise Exception(f"Error canceling task: {str(e)}")

    async def wait_for_task_completion(
        self,
        task_id: str,
        polling_interval: float = 1.0,
        timeout: Optional[float] = None,
    ) -> GetTaskResponse:
        """
        Wait for a task to complete, polling at the specified interval.

        Args:
            task_id: The ID of the task to wait for.
            polling_interval: Time in seconds between polling attempts.
            timeout: Maximum time in seconds to wait for completion. None means wait indefinitely.

        Returns:
            GetTaskResponse: The final task response when complete.

        Raises:
            TimeoutError: If the task doesn't complete within the timeout period.
            Exception: If there's an error retrieving the task status.
        """
        start_time = asyncio.get_event_loop().time()

        while True:
            response = await self.get_task(task_id)

            # Check if task is complete
            if (
                response.result
                and response.result.status
                and response.result.status.state
                in [
                    "COMPLETED",
                    "FAILED",
                    "CANCELED",
                    "completed",
                    "failed",
                    "canceled",
                ]
            ):
                return response

            # Check timeout
            if timeout is not None:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > timeout:
                    raise TimeoutError(
                        f"Task {task_id} did not complete within {timeout} seconds"
                    )

            # Wait before polling again
            await asyncio.sleep(polling_interval)
