from typing import Any

from pydantic import BaseModel


class ExecuteDatabaseResponse(BaseModel):
    command: str
    rowCount: int
    data: Any
