from dataclasses import dataclass

@dataclass
class XiaoHongShuSearchNotesItem:
    id: str
    title: str
    url: str
    likedCount: str
    
    
@dataclass
class XiaoHongShuVogueNoteItem:
    title: str
    url: str
    liked_count: int


@dataclass
class XiaoHongShuPopularNotesSearchItem:
    url: str
    title: str
    liked_count: int
    author_name: str
    author_id: str
    fan_count: int
    liked_fan_rate: float
    
    
@dataclass
class XiaoHongShuAccountNoteItem:
    title: str
    url: str
    liked_count: int