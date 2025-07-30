from dataclasses import dataclass
from typing import Optional


@dataclass
class BiliBiliHotTopicItem:
    topic: str
    url: str 


@dataclass
class BiliBiliVideoCommentsItem:
    content: str
    create_time: str


@dataclass
class BiliBiliSearchVideoItem:
    url: Optional[str]
    title: Optional[str]
    description: Optional[str]
    tag: Optional[str]
    likes: Optional[int]
    views: Optional[int]
    reviews: Optional[int]