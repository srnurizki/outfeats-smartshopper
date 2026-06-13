# <<<./ Import Libraries
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from agent.smartshopper_agent import smartshopper_agent
from memory.chat_memory import chat_message_store
from haystack_experimental.components.writers import ChatMessageWriter
from haystack_experimental.components.retrievers import ChatMessageRetriever
from haystack.dataclasses import ChatMessage
import logging
from tools.timer import timer
from tools.product_tool import _last_documents
import asyncio

# <<<./ Instantiate Logger and Dependencies
logger = logging.getLogger(__name__)
session_service = InMemorySessionService()
runner = Runner(
    agent = smartshopper_agent,
    app_name = 'SHEIN Smartshopper',
    session_service = session_service)

memory_writer = ChatMessageWriter(chat_message_store)
memory_retriever = ChatMessageRetriever(chat_message_store)

# <<<./ Get History
def get_history(session_id: str = 'default'):
    result = memory_retriever.run(chat_history_id = session_id)
    messages = result.get('messages', [])
    if not messages:
        return ''
    return '\n'.join([f'{message.role}: {message.text}' for message in messages])

# <<<./ Write Memory
def write_memory(user_message: str, agent_response: str, session_id: str = 'default'):
    memory_writer.run(
        messages = [
            ChatMessage.from_user(user_message),
            ChatMessage.from_assistant(agent_response)],
        chat_history_id = session_id)

# <<<./ Response Handler
def response_handler(user_message: str, session_id: str = 'default'):
    import tools.product_tool as pt
    try:
        asyncio.run(session_service.create_session(
            app_name='SHEIN Smartshopper',
            user_id='user',
            session_id=session_id
        ))
    except Exception:
        pass

    content = Content(role = 'user', parts = [Part(text = user_message)])

    response_text = ''
    events = runner.run(
        user_id = 'user',
        session_id = session_id,
        new_message = content)

    for event in events:
        if event.is_final_response():
            if event.content and event.content.parts:
                response_text = event.content.parts[0].text
            break

    documents = pt._last_documents.copy()
    pt._last_documents = []

    if response_text:
        write_memory(user_message, response_text, session_id)
        logger.info(f'Response written to memory for session: {session_id}')

    return response_text, documents