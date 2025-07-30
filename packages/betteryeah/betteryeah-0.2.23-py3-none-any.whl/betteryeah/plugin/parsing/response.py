from dataclasses import dataclass
from enum import Enum


@dataclass
class WebParsingItem:
    url: str
    content: str


@dataclass
class VideoParsingItem:
    BeginTime: int
    EndTime: int
    SilenceDuration: int
    SpeakerId: str
    Text: str
    ChannelId: int
    SpeechRate: int
    EmotionValue: float
    image: str = None
