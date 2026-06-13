# <<<./ Import Libraries
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack_integrations.components.retrievers.mongodb_atlas import MongoDBAtlasEmbeddingRetriever
from haystack_integrations.document_stores.mongodb_atlas import MongoDBAtlasDocumentStore
from config.settings import (
    MONGO_DB_NAME,
    COMMON_COLLECTION,
    VECTOR_SEARCH_INDEX,
    EMBEDDING_MODEL,
    GENERATOR_MODEL,
    GENERATOR_BASE_URL,
    DEEPSEEK_API,
    COMMON_TOP_K
)
from tools.timer import timer

# <<<./ Common RAG Template
COMMON_RAG_TEMPLATE = [
    ChatMessage.from_system(
        'You are a helpful customer support assistant for a fashion e-commerce platform.'),
    ChatMessage.from_user(
        """
        Your task is to answer the user question based on the provided context.
        If the context does not contain enough information to answer the question, say so.

        The question is: {{query}}

        {% if documents|length > 0 %}
        Context:
        {% for chat in documents %}
        ===========================================================
        {{loop.index}}. instruction: {{ chat.meta.instruction }}
        response: {{ chat.meta.response }}
        ===========================================================
        {% endfor %}
        {% else %}
        There is no relevant information found.
        {% endif %}

        Answer:
        """
    )
]

# <<<./ Common RAG Pipeline
class CommonsRAGPipeline:
    def __init__(self):
        self.document_store = MongoDBAtlasDocumentStore(
            database_name = MONGO_DB_NAME,
            collection_name = COMMON_COLLECTION,
            vector_search_index = VECTOR_SEARCH_INDEX,
            full_text_search_index= '')

        self.pipeline = Pipeline()
        self.pipeline.add_component('embedder', SentenceTransformersTextEmbedder(model = EMBEDDING_MODEL))
        self.pipeline.add_component('retriever', MongoDBAtlasEmbeddingRetriever(document_store = self.document_store, top_k = COMMON_TOP_K))
        self.pipeline.add_component('prompt_builder', ChatPromptBuilder(variables = ['query', 'documents'], required_variables = ['query', 'documents']))
        self.pipeline.add_component('generator', OpenAIChatGenerator(model = GENERATOR_MODEL, api_key = Secret.from_token(DEEPSEEK_API), api_base_url = GENERATOR_BASE_URL))

        self.pipeline.connect('embedder', 'retriever')
        self.pipeline.connect('retriever', 'prompt_builder.documents')
        self.pipeline.connect('prompt_builder.prompt', 'generator.messages')

    @timer
    def run(self, query: str, filter: dict = {}):
        res = self.pipeline.run(
            data = {
                'embedder' : {
                    'text' : query},
                'retriever': {
                    'filters' : filter},
                'prompt_builder' : {
                    'query' : query,
                    'template' : COMMON_RAG_TEMPLATE
                }},
            include_outputs_from = ['generator', 'prompt_builder', 'retriever'])
        print(res['prompt_builder']['prompt'])
        return res['generator']['replies'][0].text, res['retriever']['documents']

