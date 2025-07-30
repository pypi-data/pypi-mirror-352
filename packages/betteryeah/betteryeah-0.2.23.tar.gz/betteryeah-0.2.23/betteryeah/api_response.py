from dataclasses import dataclass
from typing import Optional, Generic, TypeVar

T = TypeVar('T')


@dataclass
class ApiResponse(Generic[T]):
    code: int
    message: str
    now_time: int
    success: bool
    request_id: str = None
    data: Optional[T] = None
    usage: Optional[dict] = None
