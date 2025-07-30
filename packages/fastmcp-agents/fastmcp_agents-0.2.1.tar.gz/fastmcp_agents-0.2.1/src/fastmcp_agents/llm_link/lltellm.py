import copy
import json
import os

from litellm import CustomStreamWrapper, LiteLLM, acompletion
from litellm.experimental_mcp_client.tools import transform_mcp_tool_to_openai_tool
from litellm.types.utils import ChatCompletionMessageToolCall, Function, ModelResponse, StreamingChoices
from litellm.utils import supports_function_calling
from mcp.types import Tool as MCPTool

from fastmcp_agents.conversation.types import AssistantConversationEntry, CallToolRequest, Conversation
from fastmcp_agents.errors.base import NoResponseError, UnknownToolCallError, UnsupportedFeatureError
from fastmcp_agents.errors.llm_link import ModelDoesNotSupportFunctionCallingError, ModelNotSetError
from fastmcp_agents.llm_link.base import (
    AsyncLLMLink,
)


class AsyncLitellmLLMLink(AsyncLLMLink):
    model: str

    def __init__(self, model: str | None = None, completion_kwargs: dict | None = None, client: LiteLLM | None = None) -> None:
        """Create a new Litellm LLM link.

        Args:
            model: The model to use.
            completion_kwargs: The completion kwargs to use.
            client: The Litellm client to use.
        """
        self.client = client or LiteLLM()

        if model := (model or os.getenv("MODEL")):
            self.model = model
        else:
            raise ModelNotSetError

        self.completion_kwargs = completion_kwargs or {}

        self.validate_model(model)

    @classmethod
    def validate_model(cls, model: str):
        """Validate that the model is a valid Litellm model and that it supports function calling

        Args:
            model: The model to validate.
        """
        if not supports_function_calling(model=model):
            raise ModelDoesNotSupportFunctionCallingError(model=model)

    async def _extract_tool_call_requests(
        self, response: ModelResponse
    ) -> tuple[list[ChatCompletionMessageToolCall], list[CallToolRequest]]:
        """Extract the tool calls from the response.

        Args:
            response: The response from the LLM.

        Returns:
            A tuple containing the raw tool calls and the tool call requests.
        """

        if not (choices := response.choices) or len(choices) == 0:
            raise NoResponseError(missing_item="choices", model=self.model)

        if len(choices) > 1:
            raise UnsupportedFeatureError(feature="completions returning multiple choices")

        if isinstance(choices[0], StreamingChoices):
            raise UnsupportedFeatureError(feature="streaming completions")

        choice = choices[0]

        if not (response_message := choice.message):
            raise NoResponseError(missing_item="response message", model=self.model)

        if not (tool_calls := response_message.tool_calls):
            raise NoResponseError(missing_item="tool calls", model=self.model)

        self.logger.debug(f"Response contains {len(tool_calls)} tool requests: {tool_calls}")

        tool_call_requests = []

        for tool_call in tool_calls:
            if not isinstance(tool_call, ChatCompletionMessageToolCall):
                raise UnknownToolCallError(
                    tool_name=tool_call.name, extra_info=f"Tool call is not a ChatCompletionMessageToolCall: {tool_call}"
                )

            tool_call_function: Function = tool_call.function

            if not tool_call_function.name:
                raise UnknownToolCallError(tool_name="unknown", extra_info=f"Tool call has no name: {tool_call}")

            cast_arguments = json.loads(tool_call_function.arguments) or {}

            tool_call_request = CallToolRequest(
                id=tool_call.id,
                name=tool_call_function.name,
                arguments=cast_arguments,
            )

            tool_call_requests.append(tool_call_request)

        return tool_calls, tool_call_requests

    @classmethod
    def _copy_tools(cls, tools: list[MCPTool]) -> list[MCPTool]:
        """Make a deep copy of the tools.

        Args:
            tools: The tools to copy.

        Returns:
            A deep copy of the tools.
        """
        return [copy.deepcopy(tool) for tool in tools]

    async def async_completion(
        self,
        conversation: Conversation,
        tools: list[MCPTool],
    ) -> tuple[Conversation, list[CallToolRequest]]:
        """Call the LLM with the given messages and tools.

        Args:
            messages: The messages to send to the LLM.
            tools: The tools to use.

        Returns:
            A tuple containing assistant conversation entries and their corresponding tool call requests.
        """

        # LiteLLM modifies the tool params sometimes so we deep copy them
        copied_tools = self._copy_tools(tools)

        openai_tools = [transform_mcp_tool_to_openai_tool(tool) for tool in copied_tools]

        messages = conversation.to_messages()

        model_response = await acompletion(
            messages=messages,
            model=self.model,
            **self.completion_kwargs,
            tools=openai_tools,
            tool_choice="required",
            num_retries=3,
        )

        # Make the typechecker happy
        if isinstance(model_response, CustomStreamWrapper):
            raise UnsupportedFeatureError(feature="streaming completions")

        if model_response.model_extra:
            self.token_usage += model_response.model_extra.get("usage", {}).get("total_tokens", 0)

        tool_calls, tool_call_requests = await self._extract_tool_call_requests(model_response)

        return conversation.add(
            AssistantConversationEntry(
                role="assistant",
                tool_calls=tool_calls,
            )
        ), tool_call_requests
