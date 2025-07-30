from dataclasses import dataclass
from typing import List, Union





@dataclass
class LLMAvailableModel:
    name: str
    model: str
    llm_consume_points: int