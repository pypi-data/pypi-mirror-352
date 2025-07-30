from dataclasses import dataclass


@dataclass
class GenerateImageResponse:
    data: str


@dataclass
class VisionImageResponse:
    data: str
