from dataclasses import dataclass
from typing import Optional


@dataclass
class ToutiaoHotspotItem:
    topic: str

    url: str
    heat: int
    title: Optional[str] = None
