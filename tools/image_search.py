# <<<./ Import Libraries
from database.mongo_client import get_image_cache, store_image_cache
import logging
from tools.timer import time
from dotenv import load_dotenv
from serpapi import GoogleSearch
import os

# <<<./ Instantiate Logger
logger = logging.getLogger(__name__)

# <<<./ Load API
load_dotenv()
SERP_API_KEY = os.getenv('SERP_API_KEY')

def get_product_image(product_name: str):
    try:
        params = {
            'q': product_name,
            'engine': 'google_images',
            'num': 1,
            'api_key': SERP_API_KEY
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        images = results.get('images_results', [])
        results = search.get_dict()
        print(results.keys())
        print(results.get('images_results', [])[:1])
        if images:
            return images[0].get('original')
        return None
    except Exception as e:
        logger.warning(f'Image fetch failed for {product_name}: {e.response.text}')
        return None