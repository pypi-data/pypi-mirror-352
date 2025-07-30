import asyncio
import logging
from datetime import datetime, timedelta
from typing import AsyncGenerator, Dict, List, Optional

import pyjson5
from langchain_core.messages.chat import ChatMessage
from pydantic import BaseModel, Field

from khoj.database.models import Agent, ChatMessageModel, ChatModel, KhojUser
from khoj.processor.conversation import prompts
from khoj.processor.conversation.google.utils import (
    gemini_chat_completion_with_backoff,
    gemini_completion_with_backoff,
)
from khoj.processor.conversation.utils import (
    OperatorRun,
    clean_json,
    construct_question_history,
    construct_structured_message,
    generate_chatml_messages_with_context,
    messages_to_print,
)
from khoj.utils.helpers import (
    ConversationCommand,
    is_none_or_empty,
    truncate_code_context,
)
from khoj.utils.rawconfig import FileAttachment, LocationData
from khoj.utils.yaml import yaml_dump

logger = logging.getLogger(__name__)


def extract_questions_gemini(
    text,
    model: Optional[str] = "gemini-2.0-flash",
    chat_history: List[ChatMessageModel] = [],
    api_key=None,
    api_base_url=None,
    max_tokens=None,
    location_data: LocationData = None,
    user: KhojUser = None,
    query_images: Optional[list[str]] = None,
    vision_enabled: bool = False,
    personality_context: Optional[str] = None,
    query_files: str = None,
    tracer: dict = {},
):
    """
    Infer search queries to retrieve relevant notes to answer user query
    """
    # Extract Past User Message and Inferred Questions from Conversation Log
    location = f"{location_data}" if location_data else "Unknown"
    username = prompts.user_name.format(name=user.get_full_name()) if user and user.get_full_name() else ""

    # Extract Past User Message and Inferred Questions from Chat History
    chat_history_str = construct_question_history(chat_history, query_prefix="User", agent_name="Assistant")

    # Get dates relative to today for prompt creation
    today = datetime.today()
    current_new_year = today.replace(month=1, day=1)
    last_new_year = current_new_year.replace(year=today.year - 1)

    system_prompt = prompts.extract_questions_anthropic_system_prompt.format(
        current_date=today.strftime("%Y-%m-%d"),
        day_of_week=today.strftime("%A"),
        current_month=today.strftime("%Y-%m"),
        last_new_year=last_new_year.strftime("%Y"),
        last_new_year_date=last_new_year.strftime("%Y-%m-%d"),
        current_new_year_date=current_new_year.strftime("%Y-%m-%d"),
        yesterday_date=(today - timedelta(days=1)).strftime("%Y-%m-%d"),
        location=location,
        username=username,
        personality_context=personality_context,
    )

    prompt = prompts.extract_questions_anthropic_user_message.format(
        chat_history=chat_history_str,
        text=text,
    )

    prompt = construct_structured_message(
        message=prompt,
        images=query_images,
        model_type=ChatModel.ModelType.GOOGLE,
        vision_enabled=vision_enabled,
        attached_file_context=query_files,
    )

    messages = []

    messages.append(ChatMessage(content=prompt, role="user"))
    messages.append(ChatMessage(content=system_prompt, role="system"))

    class DocumentQueries(BaseModel):
        queries: List[str] = Field(..., min_items=1)

    response = gemini_send_message_to_model(
        messages,
        api_key,
        model,
        api_base_url=api_base_url,
        response_type="json_object",
        response_schema=DocumentQueries,
        tracer=tracer,
    )

    # Extract, Clean Message from Gemini's Response
    try:
        response = clean_json(response)
        response = pyjson5.loads(response)
        response = [q.strip() for q in response["queries"] if q.strip()]
        if not isinstance(response, list) or not response:
            logger.error(f"Invalid response for constructing subqueries: {response}")
            return [text]
        return response
    except:
        logger.warning(f"Gemini returned invalid JSON. Falling back to using user message as search query.\n{response}")
        questions = [text]
    logger.debug(f"Extracted Questions by Gemini: {questions}")
    return questions


def gemini_send_message_to_model(
    messages,
    api_key,
    model,
    api_base_url=None,
    response_type="text",
    response_schema=None,
    model_kwargs=None,
    deepthought=False,
    tracer={},
):
    """
    Send message to model
    """
    model_kwargs = {}

    # Monitor for flakiness in 1.5+ models. This would cause unwanted behavior and terminate response early in 1.5 models.
    if response_type == "json_object" and not model.startswith("gemini-1.5"):
        model_kwargs["response_mime_type"] = "application/json"
        if response_schema:
            model_kwargs["response_schema"] = response_schema

    # Get Response from Gemini
    return gemini_completion_with_backoff(
        messages=messages,
        system_prompt="",
        model_name=model,
        api_key=api_key,
        api_base_url=api_base_url,
        model_kwargs=model_kwargs,
        deepthought=deepthought,
        tracer=tracer,
    )


async def converse_gemini(
    user_query: str,
    references: list[dict],
    online_results: Optional[Dict[str, Dict]] = None,
    code_results: Optional[Dict[str, Dict]] = None,
    operator_results: Optional[List[OperatorRun]] = None,
    chat_history: List[ChatMessageModel] = [],
    model: Optional[str] = "gemini-2.0-flash",
    api_key: Optional[str] = None,
    api_base_url: Optional[str] = None,
    temperature: float = 1.0,
    completion_func=None,
    conversation_commands=[ConversationCommand.Default],
    max_prompt_size=None,
    tokenizer_name=None,
    location_data: LocationData = None,
    user_name: str = None,
    agent: Agent = None,
    query_images: Optional[list[str]] = None,
    vision_available: bool = False,
    query_files: str = None,
    generated_files: List[FileAttachment] = None,
    generated_asset_results: Dict[str, Dict] = {},
    program_execution_context: List[str] = None,
    deepthought: Optional[bool] = False,
    tracer={},
) -> AsyncGenerator[str, None]:
    """
    Converse with user using Google's Gemini
    """
    # Initialize Variables
    current_date = datetime.now()

    if agent and agent.personality:
        system_prompt = prompts.custom_personality.format(
            name=agent.name,
            bio=agent.personality,
            current_date=current_date.strftime("%Y-%m-%d"),
            day_of_week=current_date.strftime("%A"),
        )
    else:
        system_prompt = prompts.personality.format(
            current_date=current_date.strftime("%Y-%m-%d"),
            day_of_week=current_date.strftime("%A"),
        )

    system_prompt += f"{system_prompt}\n\n{prompts.gemini_verbose_language_personality}"
    if location_data:
        location_prompt = prompts.user_location.format(location=f"{location_data}")
        system_prompt = f"{system_prompt}\n{location_prompt}"

    if user_name:
        user_name_prompt = prompts.user_name.format(name=user_name)
        system_prompt = f"{system_prompt}\n{user_name_prompt}"

    # Get Conversation Primer appropriate to Conversation Type
    if conversation_commands == [ConversationCommand.Notes] and is_none_or_empty(references):
        response = prompts.no_notes_found.format()
        if completion_func:
            asyncio.create_task(completion_func(chat_response=response))
        yield response
        return
    elif conversation_commands == [ConversationCommand.Online] and is_none_or_empty(online_results):
        response = prompts.no_online_results_found.format()
        if completion_func:
            asyncio.create_task(completion_func(chat_response=response))
        yield response
        return

    context_message = ""
    if not is_none_or_empty(references):
        context_message = f"{prompts.notes_conversation.format(query=user_query, references=yaml_dump(references))}\n\n"
    if ConversationCommand.Online in conversation_commands or ConversationCommand.Webpage in conversation_commands:
        context_message += f"{prompts.online_search_conversation.format(online_results=yaml_dump(online_results))}\n\n"
    if ConversationCommand.Code in conversation_commands and not is_none_or_empty(code_results):
        context_message += (
            f"{prompts.code_executed_context.format(code_results=truncate_code_context(code_results))}\n\n"
        )
    if ConversationCommand.Operator in conversation_commands and not is_none_or_empty(operator_results):
        operator_content = [
            {"query": oc.query, "response": oc.response, "webpages": oc.webpages} for oc in operator_results
        ]
        context_message += (
            f"{prompts.operator_execution_context.format(operator_results=yaml_dump(operator_content))}\n\n"
        )
    context_message = context_message.strip()

    # Setup Prompt with Primer or Conversation History
    messages = generate_chatml_messages_with_context(
        user_query,
        context_message=context_message,
        chat_history=chat_history,
        model_name=model,
        max_prompt_size=max_prompt_size,
        tokenizer_name=tokenizer_name,
        query_images=query_images,
        vision_enabled=vision_available,
        model_type=ChatModel.ModelType.GOOGLE,
        query_files=query_files,
        generated_files=generated_files,
        generated_asset_results=generated_asset_results,
        program_execution_context=program_execution_context,
    )

    logger.debug(f"Conversation Context for Gemini: {messages_to_print(messages)}")

    # Get Response from Google AI
    full_response = ""
    async for chunk in gemini_chat_completion_with_backoff(
        messages=messages,
        model_name=model,
        temperature=temperature,
        api_key=api_key,
        api_base_url=api_base_url,
        system_prompt=system_prompt,
        deepthought=deepthought,
        tracer=tracer,
    ):
        if chunk.response:
            full_response += chunk.response
        yield chunk

    # Call completion_func once finish streaming and we have the full response
    if completion_func:
        asyncio.create_task(completion_func(chat_response=full_response))
