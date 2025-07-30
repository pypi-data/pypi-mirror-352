from dataclasses import dataclass
from typing import Optional

@dataclass
class WeiboHotspotItem:
    topic: str
    heat: Optional[int] = None
    category: Optional[str] = None
