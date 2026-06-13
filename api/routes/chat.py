# <<<./ Import Libraries
from fastapi import APIRouter
from api.schemas import ChatRequest, ChatResponse
from agent.response_handler import response_handler
from api.schemas import ProductItem
import uuid
import ast
from tools.product_tool import _last_image_urls

router = APIRouter()

# <<<./ Send Chat Request to Server
@router.post('/chat', response_model=ChatResponse)
def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    response, documents = response_handler(request.message, session_id=session_id)

    products = None
    if documents:
        products = []
        for doc in documents:
            size = doc.meta.get('size', [])
            if isinstance(size, str):
                try:
                    size = ast.literal_eval(size)
                except:
                    size = []
            size_str = ', '.join([str(s) for s in size]) if isinstance(size, list) else ''
            products.append(ProductItem(
                name=doc.meta.get('name', ''),
                price=f"${doc.meta.get('price', '')}",
                meta=f"Style: {doc.meta.get('style', '-')} · Color: {doc.meta.get('color', '-')}\nSize: {size_str}",
                image_url=_last_image_urls.get(doc.meta.get('name'))
            ))

    return ChatResponse(response=response, session_id=session_id, products=products)