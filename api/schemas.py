# <<<./ Import Libraries
from pydantic import BaseModel
from typing import Optional

# <<<./ Define Structure
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

class ProductItem(BaseModel):
    name: str
    price: str
    meta: str
    image_url: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    products: Optional[list[ProductItem]] = None


