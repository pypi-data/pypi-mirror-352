from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class InsertKnowledgeResponse(BaseModel):
    file_id: Optional[int]
    file_name: Optional[str]
    partition_id: Optional[int] = None


class FileType(Enum):
    FILE = 1
    TEXT = 2
    WEBPAGE = 3
    TEMPLATE_FILE = 4
    QA = 5


class KnowledgeMatchContent(BaseModel):
    vector_id: str
    file_id: int
    file_name: str
    file_type: FileType
    mimetype: Optional[str]
    chunk_id: int
    content: str
    keywords: List[str]
    extra_info: Dict[str, Any]
    tags: Optional[List[str]] = None
    partition_id: Optional[int] = None
    partition_name: Optional[str] = None
    matched_keywords: Optional[List[str]] = None
    relevance_score: Dict[str, Optional[float]] = None

    class Config:
        extra = "ignore"


class SearchKnowledgeResponse(BaseModel):
    cost_time: float
    match_contents: List[KnowledgeMatchContent]
    usage: Optional[Any] = None
    synonym_note: Optional[str] = None

    class Config:
        extra = "ignore"




if __name__ == "__main__":
    print(SearchKnowledgeResponse.model_json_schema())
