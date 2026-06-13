# <<<./ Import Libraries
from ragas import experiment
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI
from pipelines.product_rag import ProductRAGPipeline
from pipelines.common_info_rag import CommonsRAGPipeline
from pipelines.metadata_filter import MetaDataFilterPipeline
from config.settings import DEEPSEEK_API, GENERATOR_MODEL, GENERATOR_BASE_URL, EVAL_DATASET_DIR
import asyncio
import json
import os
import logging
from tools.timer import timer

# <<<./ Instantiate Logger, RAG, and RAGAS
logger = logging.getLogger(__name__)
product_rag = ProductRAGPipeline()
common_rag = CommonsRAGPipeline()
metadata_filter = MetaDataFilterPipeline()

ragas_llm = LangchainLLMWrapper(
    ChatOpenAI(
        model = GENERATOR_MODEL,
        api_key = DEEPSEEK_API,
        base_url = GENERATOR_BASE_URL))

# <<<./ Metrics
METRICS = [faithfulness, answer_relevancy, context_precision, context_recall]
for metric in METRICS:
    metric.llm = ragas_llm

# <<<./ Load Dataset for Evaluation
def load_eval_dataset(filename: str):
    path = os.path.join(EVAL_DIR, filename)
    with open(path, 'r') as f:
        return json.load(f)

# <<<./ Experiment Definitions
@experiment(metrics=METRICS)
async def _product_experiment(row):
    query = row['query']
    filters = await asyncio.to_thread(metadata_filter.run_filter, query)
    response, documents = await asyncio.to_thread(product_rag.run_rag, query, filters)
    return {
        **row,
        'response': response,
        'contexts': [doc.content for doc in documents]}

@experiment(metrics=METRICS)
async def _commons_experiment(row):
    query = row['query']
    filters = await asyncio.to_thread(metadata_filter.run_filter, query)
    response, documents = await asyncio.to_thread(common_rag.run, query, filters)
    return {
        **row,
        'response': response,
        'contexts': [doc.content for doc in documents]
    }

# <<<./ Run Evaluation for PRODUCTS
@timer
def run_eval_product():
    samples = load_eval_dataset('product_eval.json')
    result = asyncio.run(_product_experiment.arun(samples))
    logger.info(f'Evaluation completed for Product RAG: {result}')
    return result

# <<<./ Run Evaluation for COMMONS
@timer
def run_eval_commons():
    samples = load_eval_dataset('commons_eval.json')
    result = asyncio.run(_commons_experiment.arun(samples))
    logger.info(f'Evaluation completed for Common RAG: {result}')
    return result