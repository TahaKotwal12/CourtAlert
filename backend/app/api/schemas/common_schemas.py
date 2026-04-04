from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class CommonResponse(BaseModel, Generic[T]):
    code: int
    message: str
    message_id: str
    data: Optional[T] = None
