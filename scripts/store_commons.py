# <<<./ Import Libraries
import pandas as pd
from haystack import Pipeline
from haystack.dataclasses import Document
from haystack.components.writers import DocumentWriter
from haystack.document_stores.types import DuplicatePolicy
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack_integrations.document_stores.mongodb_atlas import MongoDBAtlasDocumentStore
from database.mongo_client import store_filter_values, get_client, get_db
from config.settings import (MONGO_DB_NAME, COMMON_COLLECTION, INSTRUCTION_COLLECTION,
                             RESPONSE_COLLECTION, CATEGORY_COLLECTION, INTENT_COLLECTION, VECTOR_SEARCH_INDEX,
                             EMBEDDING_MODEL, CM_CLEANED_PATH)
from tools.timer import timer
import logging

# <<<./ Instantiate Logger
logger = logging.getLogger(__name__)

# <<<./ Load Preprocessed Data
@timer
def load_cleaned_data():
    df = pd.read_csv(CM_CLEANED_PATH, sep=';')
    return df

# <<<./ Build Documents
@timer
def build_documents(df):
    documents = [Document(content = row['instruction'],
                          meta = {'response' : row['response'], 'category' : row['category'], 'intent' : row['intent']}) for _, row in df.iterrows()]
    return documents

# <<<./ Build Store Pipelines
def build_store_pipelines(document_store: MongoDBAtlasDocumentStore):
    pipeline = Pipeline()
    pipeline.add_component('embedder', SentenceTransformersDocumentEmbedder(model=EMBEDDING_MODEL))
    pipeline.add_component('writer', DocumentWriter(document_store=document_store, policy=DuplicatePolicy.OVERWRITE))
    pipeline.connect('embedder', 'writer')
    return pipeline

# <<<./ Store Commons
BATCH_SIZE  = 3000

@timer
def store_commons(pipeline: Pipeline, documents: list[Document]):
    total = len(documents)
    batches = range(0, total, BATCH_SIZE)
    for i in batches:
        batch = documents[i:i + BATCH_SIZE]
        logger.info(f'Storing batch {i // BATCH_SIZE + 1}/{(total + BATCH_SIZE - 1) // BATCH_SIZE} ({len(batch)} docs)...')
        pipeline.run({'embedder': {'documents': batch}, 'writer': {'policy': DuplicatePolicy.SKIP}})

# <<<./ Store Filter Collection
@timer
def store_filter_collections(df):
    filters = {
        CATEGORY_COLLECTION: 'category',
        INTENT_COLLECTION: 'intent'}
    for collection_name, col in filters.items():
        values = df[col][df[col] != 'unlisted'].unique().tolist()
        store_filter_values(collection_name, values)

# <<<./ Init
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    document_store = MongoDBAtlasDocumentStore(
        database_name=MONGO_DB_NAME,
        collection_name=COMMON_COLLECTION,
        vector_search_index=VECTOR_SEARCH_INDEX,
        full_text_search_index='')

    df = load_cleaned_data()
    logger.info('Loading cleaned data...')
    documents = build_documents(df)
    logger.info('Building documents...')
    pipeline = build_store_pipelines(document_store)
    store_commons(pipeline, documents)
    logger.info('Running pipeline...')
    store_filter_collections(df)
    logger.info('Storing filters...')
    logger.info('Operation completed.')
