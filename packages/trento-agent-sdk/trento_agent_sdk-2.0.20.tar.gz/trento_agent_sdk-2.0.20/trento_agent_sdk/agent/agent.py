import json
import logging
from typing import List, Dict, Optional, Any, Literal, Annotated
from ..memory.memory import LongMemory
import openai
from pydantic import BaseModel, ConfigDict, Field

from ..tool.tool_manager import ToolManager
from .agent_manager import AgentManager

logger = logging.getLogger(__name__)


class Agent(BaseModel):
    """
    A flexible agent that can process user messages, use tools, and delegate tasks to other agents.
    
    The Agent class provides a framework for building AI assistants that can:
    - Process user messages and generate responses
    - Use tools to perform actions
    - Delegate tasks to specialized remote agents
    - Maintain conversation history in short-term and long-term memory
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = "Agent"
    model: str = "gemini-2.0-flash"
    tool_manager: ToolManager = None
    agent_manager: AgentManager = None
    long_memory: Optional[LongMemory] = None
    short_memory: List[Dict[str, str]] = []
    chat_history: List[Dict[str, str]] = []
    client: Optional[openai.OpenAI] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    final_tool: Optional[str] = None  # Name of the tool that should be called last
    user_id: str = "test_user"  # standard user id for the LongMemory
    tool_required: Literal["required", "auto"] = "required"
    validation: bool = False
    validation_tool_name: str = None
    system_prompt: str = (
        "You are a highly capable orchestrator assistant. Your primary role is to understand user requests "
        "and decide the best course of action. This might involve using your own tools or delegating tasks "
        "to specialized remote agents if the request falls outside your direct capabilities or if a remote agent "
        "is better suited for the task.\n\n"
        "ALWAYS consider the following workflow:\n"
        "1. Understand the user's request thoroughly.\n"
        "2. Check if any of your locally available tools can directly address the request. If yes, use them.\n"
        "3. If local tools are insufficient or if the task seems highly specialized, consider delegating. "
        "   Use the 'list_delegatable_agents' tool to see available agents and their capabilities.\n"
        "4. If you find a suitable agent, use the 'delegate_task_to_agent' tool to assign them the task. "
        "   Clearly formulate the sub-task for the remote agent.\n"
        "5. If no local tool or remote agent seems appropriate, or if you need to synthesize information, "
        "   respond to the user directly.\n"
        "You can have multi-turn conversations involving multiple tool uses and agent delegations to achieve complex goals.\n"
        "Be precise in your tool and agent selection. When delegating, provide all necessary context to the remote agent."
    )

    def __init__(self, **data):
        super().__init__(**data)
        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
        if not self.short_memory:
            self.short_memory = [{"role": "system", "content": self.system_prompt}]
        if self.long_memory is None:
            self.long_memory = LongMemory(user_id=self.user_id)

        if self.agent_manager is not None:
            self._register_internal_tools()

    def _register_internal_tools(self):
        """Registers tools specific to agent interaction."""
        self.tool_manager.add_tool(
            fn=self.list_delegatable_agents_tool, name="list_delegatable_agents_tool"
        )

        self.tool_manager.add_tool(
            # Parameters will be dynamically added by _convert_tools_format based on the function signature
            # or defined explicitly here if needed for more complex schemas.
            fn=self.delegate_task_to_agent_tool,
            name="delegate_task_to_agent_tool",
        )

    async def list_delegatable_agents_tool(self) -> List[Dict[str, Any]]:
        """
        Return a list with one entry per registered remote agent.

        The format mirrors AgentManager.list_delegatable_agents().
        """
        return await self.agent_manager.list_delegatable_agents()

    async def delegate_task_to_agent_tool(
        self,
        agent_url: Annotated[
            str,
            Field(
                description="URL of the remote agent to which the task should be delegated"
            ),
        ],
        message: Annotated[
            str,
            Field(description="The user request / task description to forward"),
        ],
        timeout: Annotated[
            Optional[float],
            Field(
                description="Optional timeout in seconds to wait for completion",
                examples=[30],
            ),
        ] = None,
    ) -> str:
        """
        Delegate a task to a remote agent and return the response as plain text.

        Args:
            agent_url (str): The URL endpoint of the remote agent to which the task should
                be delegated. This should be a valid HTTP/HTTPS URL pointing to an active
                agent service that can handle the delegated task.
            message (str): The user request or task description to forward to the remote
                agent. This should contain all necessary context and instructions for the
                remote agent to understand and execute the task effectively.
            timeout (Optional[float], optional): Maximum time in seconds to wait for the
                remote agent to complete the task. If not specified, uses the default
                timeout configuration. Defaults to None.

        Returns:
            str: The response from the remote agent as plain text. If the agent returns
                multiple text parts, they are concatenated with newlines for readability.
        """
        resp = await self.agent_manager.delegate_task_to_agent(
            agent_url=agent_url,
            message=message,
            timeout=timeout,
        )
        return self.agent_manager.extract_text(resp)

    def _convert_tools_format(self) -> List[Dict]:
        """
        Convert tools from the tool manager to OpenAI function format.
        
        This method retrieves all registered tools from the tool manager and converts
        them to the format expected by the OpenAI API for function calling.
        
        Returns:
            List[Dict]: List of tool definitions in OpenAI function format
        """
        tool_list = []

        try:
            # Get all registered tools
            tools = self.tool_manager.list_tools()
            for tool in tools:
                # Get the tool info already in OpenAI format
                tool_info = tool.get_tool_info()
                if tool_info:
                    tool_list.append(tool_info)
                    logger.info(f"Added tool: {tool.name}")

        except Exception as e:
            logger.error(f"Error converting tools format: {e}")

        return tool_list

    async def validate_result(self, tool_name, args):
        """
        Validate the result of a tool call and insert it into long-term memory.
        
        Args:
            tool_name (str): Name of the tool to call for validation
            args (Dict): Arguments to pass to the validation tool
            
        Returns:
            str: Serialized result of the validation tool
        """
        logger.info(f"Validation tool {tool_name} called, executing it and terminating")
        result = await self.tool_manager.call_tool(tool_name, args)
        serialized_result = ""
        try:
            # Handle different result types appropriately
            if isinstance(result, str):
                serialized_result = result
            elif isinstance(result, (list, dict, int, float, bool)):
                serialized_result = json.dumps(result)
            elif hasattr(result, "__dict__"):
                serialized_result = json.dumps(result.__dict__)
            else:
                serialized_result = str(result)

            logger.info(
                f"Tool {tool_name} returned result: {serialized_result[:100]}..."
            )
            self.long_memory.insert_into_long_memory_with_update(serialized_result)

        except Exception as e:
            logger.error(f"Error serializing tool result: {e}")
            serialized_result = str(result)
        return serialized_result

    def _find_tool_name_for_call_id(self, tool_call_id_to_find: str) -> str | None:
        if not tool_call_id_to_find:
            return None
        for msg in reversed(self.short_memory): # Search backwards
            tool_calls_in_msg = []
            if hasattr(msg, "tool_calls") and msg.tool_calls: # ChatCompletionMessage
                tool_calls_in_msg = msg.tool_calls
            elif isinstance(msg, dict) and msg.get("role") == "assistant" and msg.get("tool_calls"): # dict
                tool_calls_in_msg = msg.get("tool_calls", [])

            for tc in tool_calls_in_msg:
                current_tc_id = None
                current_tc_func_name = None
                if hasattr(tc, "id"): # ChatCompletionMessageToolCall
                    current_tc_id = tc.id
                    if hasattr(tc, "function") and hasattr(tc.function, "name"):
                        current_tc_func_name = tc.function.name
                elif isinstance(tc, dict): # dict form of tool_call
                    current_tc_id = tc.get("id")
                    current_tc_func_name = tc.get("function", {}).get("name")
                
                if current_tc_id == tool_call_id_to_find and current_tc_func_name:
                    return current_tc_func_name
        logger.warning(f"Could not find tool name for tool_call_id: {tool_call_id_to_find}")
        return None

    async def run(
        self,
        user_msg: str,
        temperature: float = 0.7,
        max_iterations: int = 30,  # Add a limit to prevent infinite loops
    ) -> str:
        """
        Run the agent with the given user message.

        Args:
            user_msg: The user's message
            temperature: Temperature for the model (randomness)
            max_iterations: Maximum number of tool call iterations to prevent infinite loops

        Returns:
            The model's final response as a string, or the output of the final tool if specified
        """

        try:
            # Build initial messages
            self.short_memory.append({"role": "user", "content": user_msg})
            self.chat_history.append({"role": "user", "content": user_msg})

            # Retrieve from long memory
            mems = self.long_memory.get_memories(user_msg, top_k=5)
            if mems:
                mem_texts = [f"- [{m['topic']}] {m['description']}" for m in mems]
                mem_block = "Relevant past memories:\n" + "\n".join(mem_texts)
                self.short_memory.append({"role": "system", "content": mem_block})

            # Get available tools
            tools = self._convert_tools_format()

            # Keep track of iterations
            iteration_count = 0
            final_response_content = None

            # Track tool calls to ensure all get responses
            tool_call_ids = set()
            responded_tool_calls = set()

            # Continue running until the model decides it's done,
            # or we reach the maximum number of iterations
            while iteration_count < max_iterations:
                iteration_count += 1
                logger.info(f"Starting iteration {iteration_count} of {max_iterations}")

                # Get response from model
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.short_memory,
                    tools=tools,
                    tool_choice=self.tool_required,
                    temperature=temperature,
                )

                # Add model's response to conversation
                self.short_memory.append(response.choices[0].message)

                # Check if the model used a tool
                if (
                    hasattr(response.choices[0].message, "tool_calls")
                    and response.choices[0].message.tool_calls
                ):
                    logger.info(
                        "Model used tool(s), executing and continuing conversation"
                    )

                    # Track all tool call IDs in this turn
                    for tool_call in response.choices[0].message.tool_calls:
                        tool_call_ids.add(tool_call.id)

                    # Process and execute each tool call
                    for tool_call in response.choices[0].message.tool_calls:
                        tool_name = tool_call.function.name
                        args = json.loads(tool_call.function.arguments)
                        args_string = tool_call.function.arguments
                        call_id = tool_call.id

                        # If this is the final tool, execute it immediately and terminate
                        if self.final_tool and tool_name == self.final_tool:
                            logger.info(
                                f"Final tool {tool_name} called, executing it and terminating"
                            )
                            try:
                                # Call the final tool directly
                                result = await self.tool_manager.call_tool(
                                    tool_name, args
                                )

                                # Directly return the result
                                logger.info(
                                    "Final tool executed successfully, returning its output as the final result"
                                )

                                serialized_result = ""
                                try:
                                    # Handle different result types appropriately
                                    if isinstance(result, str):
                                        serialized_result = result
                                    elif isinstance(
                                        result, (list, dict, int, float, bool)
                                    ):
                                        serialized_result = json.dumps(result)
                                    elif hasattr(result, "_dict_"):
                                        serialized_result = json.dumps(result._dict_)
                                    else:
                                        serialized_result = str(result)

                                    logger.info(
                                        f"Tool {tool_name} returned result: {serialized_result[:100]}..."
                                    )
                                    self.long_memory.insert_into_long_memory_with_update(
                                        serialized_result
                                    )

                                except Exception as e:
                                    logger.error(f"Error serializing tool result: {e}")
                                    serialized_result = str(result)

                                # Add tool result to the conversation
                                self.short_memory.append(
                                    {
                                        "role": "tool",
                                        "tool_call_id": call_id,
                                        "name": tool_name, # Ensure tool_name is added
                                        "content": serialized_result,
                                    }
                                )

                                # Mark this tool call as responded
                                responded_tool_calls.add(call_id)

                                self.chat_history.append(
                                    {
                                        "role": "system",
                                        "content": f"Used tool `{tool_name}` with args {args_string} that returned JSON:\n{serialized_result}",
                                    }
                                )

                                return (
                                    result
                                    if isinstance(result, str)
                                    else json.dumps(result)
                                )

                            except Exception as e:
                                error_message = (
                                    f"Error executing final tool {tool_name}: {str(e)}"
                                )
                                logger.error(error_message)
                                # Return error message if the final tool fails
                                return error_message

                        # validate result
                        if self.validation and tool_name == self.validation_tool_name:
                            self.validate_result(tool_name, args)

                        logger.info(f"Calling tool {tool_name}")
                        try:
                            result = await self.tool_manager.call_tool(tool_name, args)

                            # Properly serialize the result regardless of type
                            serialized_result = ""
                            try:
                                # Handle different result types appropriately
                                if isinstance(result, str):
                                    serialized_result = result
                                elif isinstance(result, (list, dict, int, float, bool)):
                                    serialized_result = json.dumps(result)
                                elif hasattr(result, "_dict_"):
                                    serialized_result = json.dumps(result._dict_)
                                else:
                                    serialized_result = str(result)

                                logger.info(
                                    f"Tool {tool_name} returned result: {serialized_result[:100]}..."
                                )
                                self.long_memory.insert_into_long_memory_with_update(
                                    serialized_result
                                )

                            except Exception as e:
                                logger.error(f"Error serializing tool result: {e}")
                                serialized_result = str(result)

                            # Add tool result to the conversation
                            self.short_memory.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": call_id,
                                    "name": tool_name,  # Add the tool name to prevent "function_response.name: Name cannot be empty" errors
                                    "content": serialized_result,
                                }
                            )

                            # Mark this tool call as responded
                            responded_tool_calls.add(call_id)

                            self.chat_history.append(
                                {
                                    "role": "system",
                                    "content": f"Used tool `{tool_name}` with args {args_string} that returned JSON:\n{serialized_result}",
                                }
                            )
                        except Exception as e:
                            error_message = f"Error calling tool {tool_name}: {str(e)}"
                            logger.error(error_message)
                            self.short_memory.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": call_id,
                                    "name": tool_name,  # Ensure tool_name is added here as well
                                    "content": json.dumps({"error": error_message}),
                                }
                            )

                            # Mark this tool call as responded even if there was an error
                            responded_tool_calls.add(call_id)
                else:
                    # If no tool was called, save the response content and break
                    final_response_content = response.choices[0].message.content
                    logger.info("Model did not use tools, conversation complete")
                    break

                # Check if all tool calls have responses
                if self._ensure_all_tool_calls_have_responses(tool_call_ids, responded_tool_calls):
                    # Update the responded_tool_calls set after adding the missing responses
                    responded_tool_calls = responded_tool_calls.union(tool_call_ids)

            # If we've reached the maximum number of iterations, log a warning
            if iteration_count >= max_iterations:
                logger.warning(
                    f"Reached maximum number of iterations ({max_iterations})"
                )
                # Append a message to let the model know it needs to wrap up
                self.short_memory.append(
                    {
                        "role": "system",
                        "content": "You've reached the maximum number of allowed iterations. Please provide a final response based on the information you have.",
                    }
                )

            # Final check for any missed tool call responses before completing
            self._ensure_all_tool_calls_have_responses(tool_call_ids, responded_tool_calls)
            
            # Save chat history to long memory
            self.long_memory.insert_into_long_memory_with_update(self.chat_history)

            # If we already have a final response (model didn't use tools), return it
            if final_response_content is not None:
                # Ensure we never return empty content
                return final_response_content if final_response_content else "I've processed your request, but don't have additional information to provide."

            # Otherwise, get a final response from the model
            try:
                # Filter out any messages with empty content to prevent API errors
                filtered_memory = []
                for msg in self.short_memory:
                    # Handle different message types (dict vs ChatCompletionMessage)
                    if isinstance(msg, dict):
                        # For tool messages, ensure name field is present
                        if msg.get("role") == "tool":
                            msg_copy = msg.copy()
                            if not msg_copy.get("name"):
                                # Attempt to find the tool name from previous assistant messages
                                tool_name_from_history = self._find_tool_name_for_call_id(msg_copy.get("tool_call_id"))
                                if tool_name_from_history:
                                    msg_copy["name"] = tool_name_from_history
                                else:
                                    logger.warning(f"Could not find tool name for tool_call_id {msg_copy.get('tool_call_id')} during final response filtering. Using 'unknown_tool'.")
                                    msg_copy["name"] = "unknown_tool" # Add missing name field
                            filtered_memory.append(msg_copy)
                        elif msg.get("content") or msg.get("tool_calls"):  # Only add non-tool messages if they have content or tool_calls
                            filtered_memory.append(msg)
                    elif hasattr(msg, "role") and msg.role == "tool":
                        msg_dict = {
                            "role": msg.role,
                            "content": msg.content if hasattr(msg, "content") else None, # Ensure content is present
                            "tool_call_id": getattr(msg, "tool_call_id", None) # Ensure tool_call_id is present
                        }
                        tool_name = getattr(msg, "name", None)
                        if not tool_name:
                            # Attempt to find the tool name from previous assistant messages
                            tool_name_from_history = self._find_tool_name_for_call_id(msg_dict["tool_call_id"])
                            if tool_name_from_history:
                                msg_dict["name"] = tool_name_from_history
                            else:
                                logger.warning(f"Could not find tool name for tool_call_id {msg_dict['tool_call_id']} (ChatCompletionMessage) during final response filtering. Using 'unknown_tool'.")
                                msg_dict["name"] = "unknown_tool"
                        else:
                            msg_dict["name"] = tool_name
                        filtered_memory.append(msg_dict)
                    elif (hasattr(msg, "content") and msg.content) or (hasattr(msg, "tool_calls") and msg.tool_calls):
                        # Convert ChatCompletionMessage to dict for compatibility
                        msg_dict = {
                            "role": msg.role,
                        }
                        if hasattr(msg, "content") and msg.content:
                            msg_dict["content"] = msg.content
                        if hasattr(msg, "tool_calls") and msg.tool_calls:
                            # Ensure tool_calls are correctly formatted as list of dicts
                            msg_dict["tool_calls"] = []
                            for tc in msg.tool_calls:
                                tc_dict = {"id": tc.id, "type": tc.type}
                                if hasattr(tc, "function"):
                                    tc_dict["function"] = {"name": tc.function.name, "arguments": tc.function.arguments}
                                msg_dict["tool_calls"].append(tc_dict)
                        
                        filtered_memory.append(msg_dict)
                
                if not filtered_memory:
                    logger.warning("All messages had empty content, using a default system message")
                    filtered_memory = [{"role": "system", "content": "Please provide a response based on our conversation."}]
                
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=filtered_memory,
                    temperature=temperature,
                )
                response_content = final_response.choices[0].message.content
                # Ensure we never return empty content
                return response_content if response_content else "I've processed your request, but don't have additional information to provide."
            except Exception as e:
                logger.error(f"Error getting final response: {e}")
                # Log more details about the error for debugging
                logger.error(f"Error details: {str(e)}")
                return "I apologize, but I encountered an error while generating my final response."

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error running agent: {error_msg}")
            
            # Check for specific OpenAI function call errors
            if "function response parts" in error_msg and "function call parts" in error_msg:
                logger.error("OpenAI function call/response mismatch detected")
                # Try to recover by ensuring all tool calls have responses
                try:
                    self._ensure_all_tool_calls_have_responses(tool_call_ids, responded_tool_calls)
                    # Try one more time to get a final response
                    final_response = self.client.chat.completions.create(
                        model=self.model,
                        messages=self.short_memory,
                        temperature=temperature,
                    )
                    return final_response.choices[0].message.content
                except Exception as recovery_error:
                    logger.error(f"Recovery attempt failed: {str(recovery_error)}")
                    return "I encountered an error with function calls. Please try again with a simpler request."
            
            # Check for empty parts error
            if "contents.parts must not be empty" in error_msg or "function_response.name: Name cannot be empty" in error_msg or "Name cannot be empty" in error_msg:
                logger.error("Empty message parts or function response name detected in the request")
                try:
                    # Filter out messages with empty content, handling both dict and ChatCompletionMessage objects
                    filtered_memory = []
                    for msg in self.short_memory:
                        # Handle different message types (dict vs ChatCompletionMessage)
                        if isinstance(msg, dict):
                            if msg.get("role") == "tool":
                                # Ensure tool messages always have a name
                                msg_copy = msg.copy()
                                if not msg_copy.get("name"):
                                    msg_copy["name"] = "unknown_tool"
                                filtered_memory.append(msg_copy)
                            elif msg.get("content"):
                                filtered_memory.append(msg)
                        elif hasattr(msg, "content") and msg.content:
                            # Convert ChatCompletionMessage to dict for compatibility
                            msg_dict = {
                                "role": getattr(msg, "role", "user"),
                                "content": msg.content
                            }
                            # For tool messages, ensure name and tool_call_id are present
                            if getattr(msg, "role", "") == "tool":
                                tool_name = getattr(msg, "name", None) or getattr(msg, "function_name", None)
                                msg_dict["name"] = tool_name if tool_name else "unknown_tool"
                                # Include tool_call_id if present
                                if hasattr(msg, "tool_call_id"):
                                    msg_dict["tool_call_id"] = msg.tool_call_id
                            filtered_memory.append(msg_dict)
                            
                    if not filtered_memory:
                        return "I'm having trouble processing this request due to empty content. Please try a different request."
                    
                    # Try one more time with filtered messages
                    final_response = self.client.chat.completions.create(
                        model=self.model,
                        messages=filtered_memory,
                        temperature=temperature,
                    )
                    return final_response.choices[0].message.content
                except Exception as recovery_error:
                    logger.error(f"Recovery attempt for empty parts failed: {str(recovery_error)}")
                    return "I encountered an error with message formatting. Please try again with a different request."
            
            return f"Error: {error_msg}"

    def _ensure_all_tool_calls_have_responses(self, tool_call_ids, responded_tool_calls):
        """
        Ensure all tool calls have corresponding responses to prevent OpenAI API errors.

        Args:
            tool_call_ids: Set of tool call IDs that need responses
            responded_tool_calls: Set of tool call IDs that have received responses

        Returns:
            bool: True if any missing responses were added, False otherwise
        """
        if tool_call_ids != responded_tool_calls:
            missing_calls = tool_call_ids - responded_tool_calls
            logger.warning(f"Missing responses for tool calls: {missing_calls}")
            # Add dummy responses for any missing tool calls to prevent API errors
            for missing_id in missing_calls:
                self.short_memory.append(
                    {
                        "role": "tool",
                        "tool_call_id": missing_id,
                        "name": "unknown_tool",  # Add a name to prevent "function_response.name: Name cannot be empty" errors
                        "content": json.dumps({"error": "No response generated for this tool call"}),
                    }
                )
            return True
        return False
