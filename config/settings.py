# <<<./ Import Libraries
import os
from dotenv import load_dotenv

load_dotenv()

# <<<./ MongoDB
MONGO_CONNECTION_STRING = os.getenv('MONGO_CONNECTION_STRING')
MONGO_DB_NAME = 'sheinData'
PRODUCT_COLLECTION = 'products'
COMMON_COLLECTION = 'commons'
FABRICS_COLLECTION = 'fabrics'
COLORS_COLLECTION = 'colors'
STYLES_COLLECTION = 'styles'
PATTERNS_COLLECTION = 'patterns'
IMAGE_CACHE_COLLECTION = 'image_cache'
CHAT_COLLECTION = 'chat'
INSTRUCTION_COLLECTION = 'instructions'
RESPONSE_COLLECTION = 'responses'
CATEGORY_COLLECTION = 'categories'
INTENT_COLLECTION = 'intents'

# <<<./ APIs
DEEPSEEK_API = os.getenv('DEEPSEEK_API')
GOOGLE_CSE_API_KEY = os.getenv('GOOGLE_CSE_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')

# <<<./ Models
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
GENERATOR_MODEL = 'deepseek-v4-flash'
GENERATOR_BASE_URL = 'https://api.deepseek.com'
FILTER_GENERATOR_MODEL = 'deepseek-v4-flash'

# <<<./ Retrieval Top-K
PRODUCT_TOP_K = 5
COMMON_TOP_K = 3

# <<<./ Vector Search
VECTOR_SEARCH_INDEX = 'vector_index'

# <<<./ Paths
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
SH_RAW_PATH = os.path.join(DATA_DIR, 'shein.csv')
SH_CLEANED_PATH = os.path.join(DATA_DIR, 'shein-clean.csv')
CM_RAW_PATH = os.path.join(DATA_DIR, 'commons.csv')
CM_CLEANED_PATH = os.path.join(DATA_DIR, 'commons-clean.csv')
EVAL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'evaluation')
REPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'monitoring', 'reports')

# <<<./ FastAPI
ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')
