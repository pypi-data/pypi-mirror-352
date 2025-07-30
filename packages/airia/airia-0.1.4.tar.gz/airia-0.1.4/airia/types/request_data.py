from typing import Any, Dict

from pydantic import BaseModel


class RequestData(BaseModel):
    url: str
    payload: Dict[str, Any]
    headers: Dict[str, Any]
    correlation_id: str
