# <<<./ Import Libraries
from google.adk.tools import FunctionTool
from pipelines.paraphraser import ParaphraserPipeline
from pipelines.metadata_filter import MetaDataFilterPipeline
from pipelines.product_rag import ProductRAGPipeline
from tools.image_search import get_product_image
from memory.chat_memory import chat_message_store
import logging
from tools.timer import timer

# <<<./ Instantiate Logger and Functions
logger = logging.getLogger(__name__)
paraphraser = ParaphraserPipeline(chat_message_store)
metadata_filter = MetaDataFilterPipeline()
product_rag = ProductRAGPipeline()
_last_documents = []
_last_image_urls = {}

# <<<./ Product Recommendation
@timer
def product_recommendation(query: str):
    """
    Use this tool when the user asks for product recommendations,
    wants to find fashion items, or has queries about specific clothing,
    accessories, or products. This tool searches the product catalog
    and returns a list of matching products with details and images.
    """
    global _last_documents, _last_image_urls

    paraphrased_query = paraphraser.run_paraphraser(query)
    logger.info(f'Paraphrased query: {paraphrased_query}')

    filters = metadata_filter.run(paraphrased_query)
    logger.info(f'Generated filters: {filters}')

    response, documents = product_rag.run(paraphrased_query, filters)
    logger.info(f'Retrieved {len(documents)} documents')

    _last_documents = documents or []
    _last_image_urls.clear()

    for doc in _last_documents:
        product_name = doc.meta.get('name')
        if product_name:
            image_url = get_product_image(product_name)
            if image_url:
                _last_image_urls[product_name] = image_url

    if _last_image_urls:
        response += '\n\nProduct Images:'
        for name, url in _last_image_urls.items():
            response += f'\n{name}: {url}'

    return response

# <<<./ Define Tool
product_tool = FunctionTool(product_recommendation)