# <<<./ Import Libraries
from google.adk.tools import FunctionTool
from pipelines.metadata_filter import MetaDataFilterPipeline
from pipelines.common_rag import CommonsRAGPipeline
import logging
from tools.timer import timer

# <<<./ Instantiate Logger and Functions
logger = logging.getLogger(__name__)
metadata_filter = MetaDataFilterPipeline()
common_rag = CommonsRAGPipeline()

@timer
def common_information(query: str):
    """
    Use this tool when the user asks general questions about
    the shopping process such as shipping, payment methods,
    order tracking, returns, refunds, or any other customer
    support related questions. Do not use this tool for
    product recommendations.
    """

    filters = metadata_filter.run(query)
    logger.info(f'Generated filters: {filters}')

    response = common_rag.run(query, filters)
    return response

# <<<./ Define Tool
common_tool = FunctionTool(common_information)
