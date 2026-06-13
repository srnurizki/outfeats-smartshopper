# <<<./ Import Libraries
from haystack import Pipeline
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.utils import Secret
from haystack.components.builders import ChatPromptBuilder, PromptBuilder
from haystack.components.joiners import ListJoiner
from haystack.dataclasses import ChatMessage
from haystack_experimental.components.retrievers import ChatMessageRetriever
from haystack_experimental.components.writers import ChatMessageWriter
from config.settings import GENERATOR_MODEL, GENERATOR_BASE_URL
from memory.chat_memory import chat_message_store
from typing import List
import os
from dotenv import load_dotenv
from tools.timer import timer

# <<<./ Load Environment
load_dotenv()
DEEPSEEK_API = os.getenv('DEEPSEEK_API')

# <<<./ Build Paraphraser Pipeline
class ParaphraserPipeline:
    def __init__(self, chat_message_store):
        self.chat_message_store = chat_message_store
        self.memory_retriever = ChatMessageRetriever(chat_message_store)
        self.memory_writer = ChatMessageWriter(chat_message_store)
        self.pipeline = Pipeline()
        self.pipeline.add_component('prompt_builder', ChatPromptBuilder(variables = ['query', 'memories'], required_variables = ['query']))
        self.pipeline.add_component('generator', OpenAIChatGenerator(model=GENERATOR_MODEL, api_key=Secret.from_token(DEEPSEEK_API), api_base_url=GENERATOR_BASE_URL))
        self.pipeline.add_component('memory_retriever', self.memory_retriever)
        self.pipeline.add_component('joiner', ListJoiner(List[ChatMessage]))
        self.pipeline.add_component('memory_writer', self.memory_writer)

        self.pipeline.connect('prompt_builder.prompt', 'generator.messages')
        self.pipeline.connect('memory_retriever', 'prompt_builder.memories')
        self.pipeline.connect('generator.replies', 'joiner')
        self.pipeline.connect('joiner', 'memory_writer')

    @timer
    def run_paraphraser(self, query):
        messages = [
            ChatMessage.from_system(
                'You are a helpful assistant that paraphrases user queries based on previous conversations.'),
            ChatMessage.from_user(
                """
                Please paraphrase the following query based on the conversation history provided below. If the conversation history is empty, please return the query as is.
                history:
                {% for memory in memories %}
                    {{memory.text}}
                {% endfor %}
                query: {{query}}
                answer:
                """)]

        res = self.pipeline.run(
            data = {
                'prompt_builder': {
                    'query' : query,
                    'template' : messages},
                'memory_retriever': {
                    'chat_history_id' : 'default'},
                'joiner' : {
                    'values' : [ChatMessage.from_user(query)]},
                'memory_writer': {
                    'chat_history_id': 'default'}
                },
            include_outputs_from = ['generator'])
        print('Pipeline Input', query)
        return res['generator']['replies'][0].text

# <<<./ Build Chat History Pipeline
class ChatHistoryPipeline:
    def __init__(self, chat_message_store):
        self.chat_message_store = chat_message_store
        self.pipeline = Pipeline()
        self.pipeline.add_component('memory_retriever', ChatMessageRetriever(chat_message_store))
        self.pipeline.add_component('prompt_builder', PromptBuilder(variables = ['memories'], required_variables = ['memories'], template = """
        Previous Conversation History:
        {% for memory in memories %}
            {{memory.text}}
        {% endfor %}
        """))
        self.pipeline.connect('memory_retriever', 'prompt_builder.memories')

    @timer
    def run_history(self):
        res = self.pipeline.run(
            data = {
                'memory_retriever': {
                    'chat_history_id' : 'default'}
            }, include_outputs_from = ['prompt_builder'])
        return res['prompt_builder']['prompt']