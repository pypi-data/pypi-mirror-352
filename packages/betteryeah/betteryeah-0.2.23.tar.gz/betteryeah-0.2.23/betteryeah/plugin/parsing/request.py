from enum import Enum


class ArticleParsingModel(Enum):
    Kimi = "Kimi"
    Claude = "Claude"


class AnalysisModeType(Enum):
    ScreenshotAndAudio = 0
    OnlyAudio = 1


class ExcelOutputType(Enum):
    HTML = 1
    JSON = 2


class ResultType(Enum):
    TEXT = "text"
    WORD = "word"
