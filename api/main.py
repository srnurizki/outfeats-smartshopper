# <<<./ Import Libraries
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.chat import router
from dotenv import load_dotenv
from config.settings import ORIGINS

load_dotenv()
ORIGINS = ORIGINS

# <<<./ Initialize FastAPI App
app = FastAPI(title='SmartShopper Assistant API')

# <<<./ Define Middleware for Endpoint <-> Client
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_methods=['*'],
    allow_headers=['*'])

app.include_router(router)

# <<<./ Check Server Activity Status
@app.get('/health')
def health():
    return {'status': 'OK'}
