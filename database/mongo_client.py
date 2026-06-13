# <<< ./ Import Libraries
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone
from config.settings import MONGO_CONNECTION_STRING, MONGO_DB_NAME, IMAGE_CACHE_COLLECTION

# <<<./ Instantiate Client
_client: MongoClient | None = None

# <<<./ Get Client Connection
def get_client():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_CONNECTION_STRING)
    return _client

# <<<./ Get DB Connection
def get_db():
    return get_client()[MONGO_DB_NAME]

# <<<./ Fetch Collection
def get_collection(collection_name: str):
    return get_db()[collection_name]

# <<<./ Fetch Filter Values
def get_filter_values(collection_name: str):
    collection = get_collection(collection_name)
    return [doc['name'] for doc in collection.find({}, {'_id' : 0, 'name' : 1})]

# <<<./ Store Filter Values to DB
def store_filter_values(collection_name: str, values: list[str]):
    collection = get_collection(collection_name)
    collection.create_index([('name', ASCENDING)], unique = True)
    for value in values:
        try:
            collection.update_one(
                {'name' : value},
                {'$setOnInsert' : {'name' : value}},
                upsert=True)
        except DuplicateKeyError:
            pass
    return None

# <<<./ Get Image Cache from Google Search API
def get_image_cache(product_name: str):
    collection = get_collection(IMAGE_CACHE_COLLECTION)
    doc = collection.find_one({'product_name' : product_name})
    return doc['image_url'] if doc else None

# <<<./ Store Image Cache to DB
def store_image_cache(product_name: str, image_url: str):
    collection = get_collection(IMAGE_CACHE_COLLECTION)
    collection.update_one(
        {'product_name' : product_name},
        {'$set' : {
            'image_url' : image_url,
            'cached_at' : datetime.now(timezone.utc)
        }}, upsert = True)
    return None