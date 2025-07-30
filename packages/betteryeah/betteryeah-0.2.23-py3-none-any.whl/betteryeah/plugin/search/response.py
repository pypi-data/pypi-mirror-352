from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel

@dataclass
class SearchItem:
    title: str
    url: str
    snippet: str
    index: int
    content: Optional[str] = None
    icon: Optional[str] = None
    name: Optional[str] = None



class FeloSearchResponse(BaseModel):
    success: bool
    requestId: str
    webPages: dict
    images: Optional[dict] = None


class AiSearchResponse(BaseModel):
    success: bool
    requestId: str
    messages: list[dict] = []

