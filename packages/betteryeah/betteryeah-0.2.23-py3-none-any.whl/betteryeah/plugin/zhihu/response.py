from dataclasses import dataclass
from typing import Optional


@dataclass
class ZhihuRealtimeHotspotsItem:
    topic: str
    url: str
    heat: str
    excerpt: str


@dataclass
class ZhiHuContentSearchItem:
    content: str
    title: str
    create_time: Optional[str] = None
