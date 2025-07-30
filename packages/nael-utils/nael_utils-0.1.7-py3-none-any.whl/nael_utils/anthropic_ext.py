import os
from typing import Optional, Type, TypeVar, Literal, List

from pydantic import BaseModel, SecretStr

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_core.output_parsers import JsonOutputParser

T = TypeVar('T', bound=BaseModel)


def call_claude(
    prompt: str,
    format_model: Type[T],
    model_type: Literal["sonnet", "opus"] = "sonnet",
    system_prompt: str = "",
    api_key: Optional[SecretStr] = None,
    additional_messages: Optional[List[BaseMessage]] = None,
) -> T:
    """
    Generic function to ask for Claude's inference. Return value will be in format_model
    :param prompt: The prompt to send to Claude
    :param format_model: Pydantic model to structure the response
    :param model_type: Claude model to use
    :param system_prompt: System prompt to set context
    :param max_tokens: Maximum tokens in response
    :param api_key: Anthropic API key
    :return: Parsed response as format_model instance
    """

    model = f"claude-{model_type}-4-0"

    if api_key is None:
        _api_key = os.getenv("ANTHROPIC_API_KEY", None)

        if _api_key is None:
            raise ValueError("ANTHROPIC_API_KEY is not set")
        
        api_key = SecretStr(_api_key)

    chat = ChatAnthropic(
        api_key=api_key, 
        model_name=model,
        timeout=None,
        stop=None,
    )

    parser = JsonOutputParser(pydantic_object=format_model)
    format_instructions = parser.get_format_instructions()
    _prompt = f"Answer the user query.\n{format_instructions}\n{prompt}\n"
    messages: List[BaseMessage] = [
        HumanMessage(
            content=[
                {"type": "text", "text": _prompt},
            ]
        )
    ]

    if system_prompt:
        messages.insert(0, SystemMessage(content=system_prompt))

    if additional_messages:
        messages.extend(additional_messages)

    text_result = chat.invoke(messages)
    result = parser.invoke(text_result)

    return format_model.model_validate(result)
