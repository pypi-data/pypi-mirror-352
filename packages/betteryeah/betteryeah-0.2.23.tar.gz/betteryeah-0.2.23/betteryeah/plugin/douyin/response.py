from dataclasses import dataclass
from typing import List, Optional


@dataclass
class DouyinVideoAnalysisItemDetail:
    startTime: int
    endTime: int
    text: str
    image: str


@dataclass
class DouyinVideoAnalysisItem:
    title: Optional[str]
    tags: Optional[List[str]]
    data: Optional[List[DouyinVideoAnalysisItemDetail]]


@dataclass
class DouyinTrendingTopicItem:
    topic: str
    heat: int
    url: str
