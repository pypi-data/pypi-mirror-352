import logging
import asyncio
from .models.Task import Task, TaskStatus, TaskState, Message, Artifact
from datetime import datetime

from .models.Types import (
    GetTaskRequest,
    GetTaskResponse,
    CancelTaskRequest,
    CancelTaskResponse,
    SendTaskRequest,
    SendTaskResponse,
)

logger = logging.getLogger(__name__)


class TaskManager:
    def __init__(self):
        self.tasks: dict[str, Task] = {}

    def on_get_task(self, request: GetTaskRequest) -> GetTaskResponse:
        logger.info(f"Getting task {request.params.id}")
        task = self.tasks.get(request.params.id)
        if task is None:
            return GetTaskResponse(id=request.id, error="Task not found")

        return GetTaskResponse(id=request.id, result=task)

    def on_cancel_task(self, request: CancelTaskRequest) -> CancelTaskResponse:
        logger.info(f"Cancelling task {request.params.id}")
        task = self.tasks.get(request.params.id)
        if task is None:
            return CancelTaskResponse(id=request.id, error="Task not found")

        return CancelTaskResponse(id=request.id)

    async def _update_task(
        self,
        task_id: str,
        task_state: TaskState,
        response_text: str,
    ) -> Task:
        task = self.tasks[task_id]
        from .models.Task import TextPart

        # Create proper TextPart object instead of raw dictionary
        agent_response_parts = [TextPart(type="text", text=response_text)]

        task.status = TaskStatus(
            state=task_state,
            message=Message(
                role="agent",
                parts=agent_response_parts,
            ),
            timestamp=datetime.now(),
        )
        task.artifacts = [
            Artifact(
                parts=agent_response_parts,
            )
        ]
        return task

    async def _invoke(self, request: SendTaskRequest, agent) -> str:
        """
        Invoke the agent with the task request and return the response content.
        Implements retry logic and better error handling.

        Args:
            request: The task request containing the user message
            agent: The agent instance to invoke

        Returns:
            The agent's response as a string
        """
        task_send_params = request.params
        query = self._get_user_query(task_send_params)
        
        # Configuration for retry logic
        max_retries = 3
        retry_delay = 1.0
        last_exception = None
        
        # Instead of a single try/except, implement retry logic with exponential backoff
        for attempt in range(max_retries):
            try:
                # The agent.run() returns the model's final response as a string
                result = await agent.run(query)
                return result
            except Exception as e:
                last_exception = e
                error_msg = str(e)
                
                # Special handling for known error conditions
                if "number of function response parts" in error_msg:
                    logger.error("OpenAI function call/response mismatch detected. This usually happens when not all function calls receive responses.")
                    # This is a critical error that won't be fixed by retrying
                    return "Error: OpenAI function call error - Please ensure that the number of function response parts is equal to the number of function call parts. Check your agent implementation to ensure all tool calls receive responses."
                
                # Decide if this error is retryable
                retryable_errors = [
                    "rate limit", 
                    "timeout", 
                    "connection", 
                    "socket", 
                    "network",
                    "too many requests",
                    "server error",
                    "5xx",
                    "load"
                ]
                
                is_retryable = any(err_text in error_msg.lower() for err_text in retryable_errors)
                
                if is_retryable and attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Retryable error: {error_msg}. Retrying in {wait_time:.1f}s ({attempt+1}/{max_retries})...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Error invoking agent: {e}")
                    return f"Error: {error_msg}"
        
        # This should only be reached if all retries failed
        return f"Error: Failed after {max_retries} attempts. Last error: {str(last_exception)}"

    async def on_send_task(self, request: SendTaskRequest, agent) -> SendTaskResponse:
        task = self.tasks.get(request.params.id)
        if task is None:
            task = Task(
                id=request.params.id,
                sessionId=request.params.sessionId,
                status=TaskStatus(
                    state=TaskState.SUBMITTED,
                    message=request.params.message,
                    timestamp=datetime.now(),
                ),
                history=[request.params.message],
            )
            self.tasks[request.params.id] = task

            # Update task to working state
            await self._update_task(
                task_id=request.params.id,
                task_state=TaskState.WORKING,
                response_text="Processing your request...",
            )

            # Invoke the agent
            content = await self._invoke(request, agent)

            # Update task to completed state
            task = await self._update_task(
                task_id=request.params.id,
                task_state=TaskState.COMPLETED,
                response_text=content,
            )

            return SendTaskResponse(id=request.id, result=task)

        # If task already exists, return current state
        return SendTaskResponse(id=request.id, result=task)

    def _get_user_query(self, task_params):
        """Extract user query from task parameters."""
        if hasattr(task_params, "message") and task_params.message:
            # Extract text parts from the message
            parts = (
                task_params.message.parts
                if hasattr(task_params.message, "parts")
                else []
            )
            query = []
            for part in parts:
                # Check if it's a TextPart object with text attribute
                if (
                    hasattr(part, "type")
                    and part.type == "text"
                    and hasattr(part, "text")
                    and part.text is not None
                ):
                    query.append(part.text)
                # Fallback for dictionary-style parts
                elif (
                    isinstance(part, dict)
                    and part.get("type") == "text"
                    and part.get("text") is not None
                ):
                    query.append(part.get("text", ""))

            if not query:
                # If no valid text parts were found, log a warning
                logger.warning("No valid text parts found in the message")
                return "No query provided"

            return " ".join(query)

        logger.warning("No message found in task parameters")
        return "No query provided"
