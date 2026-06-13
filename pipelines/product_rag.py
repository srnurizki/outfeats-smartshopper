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
    PRODUCT_COLLECTION,
    VECTOR_SEARCH_INDEX,
    EMBEDDING_MODEL,
    GENERATOR_MODEL,
    GENERATOR_BASE_URL,
    DEEPSEEK_API,
    PRODUCT_TOP_K
)
from tools.timer import timer

# <<<./ Product RAG Template
PRODUCT_RAG_TEMPLATE = [
    ChatMessage.from_system(
        'You are a helpful fashion shop assistant that will give products recommendation based on user query and metadata filtering.'),
        ChatMessage.from_user(
        """
        Your task is to generate a list of products that best match the query.
        The output should be a list of products in the following format:

        <summary_of_query>
        <index>. <product_name> 
        Price: <product_price>
        Fabric: <product_fabric>
        Pattern: <product_pattern>
        Size: <product_size>
        Style: <product_style>
        Recommendation: <product_recommendation>

        From the format above, you should pay attention to the following:
        1. <summary_of_query> should be a short summary of the query.
        2. <index> should be a number starting from 1.
        3. <product_name> should be the name of the product, this product name can be found from the product_name field.
        4. <product_price> should be the price of the product, this product price can be found from the product_price field.
        5. <product_fabric> should be the fabric material of the product, this product fabric material can be found from the product_fabric field.
        6. <product_pattern> should be the pattern of the product, this product pattern can be found from the product_pattern field.
        7. <product_brand> should be the brand of the product, this product brand can be found from the product_brand field.
        8. <product_size> should be the size of the product, this product size can be found from the product_size field.
        9. <product_recommendation> should be the recommendation of the product, you should give a recommendation why this product is recommended, please pay attentation to the product_content field. 

        You should only return the list of products that best match the query, do not return any other information.
        If there is no matching product below, please say so.

        The query is: {{query}}
        {% if documents|length > 0 %}
        the products are:
        {% for product in documents %}
        ===========================================================
        {{loop.index}}. product_name: {{ product.meta.name }}
        product_price: {{ product.meta.price }}
        product_fabric: {{ product.meta.fabric }}
        product_pattern: {{ product.meta.pattern }}
        product_brand: {{ product.meta.brand }}
        product_content: {{ product.content}}
        {% endfor %}

        ===========================================================
        {% else %}
        There is no matching product.
        {% endif %}

        Answer:

        """
        )]

# <<<./ Product RAG Pipeline
class ProductRAGPipeline:
    def __init__(self):
        self.document_store = MongoDBAtlasDocumentStore(
            database_name = MONGO_DB_NAME,
            collection_name = PRODUCT_COLLECTION,
            vector_search_index = VECTOR_SEARCH_INDEX,
            full_text_search_index= '')

        self.pipeline = Pipeline()
        self.pipeline.add_component('embedder', SentenceTransformersTextEmbedder(model = EMBEDDING_MODEL))
        self.pipeline.add_component('retriever', MongoDBAtlasEmbeddingRetriever(document_store = self.document_store, top_k = PRODUCT_TOP_K))
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
                    'template' : PRODUCT_RAG_TEMPLATE
                }},
            include_outputs_from = ['generator', 'prompt_builder', 'retriever'])
        print(res['prompt_builder']['prompt'])
        return res['generator']['replies'][0].text, res['retriever']['documents']

