import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ApiException(Exception):
    def __init__(self, http_code: int, **options) -> None:
        self.http_code = http_code
        for key, value in options.items():
            setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

    def to_json(self) -> str:
        return json.dumps(self.__dict__)


class ValidationErrorResult(BaseModel):
    loc: list
    type: str
    msg: str
    ctx: Optional[Dict[str, Any]]


class ValidationErrorResponses(BaseModel):
    """No matter how many errors there are, an exception will be raised."""

    results: List[ValidationErrorResult]
