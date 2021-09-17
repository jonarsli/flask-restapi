import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ApiException(Exception):
    def __init__(self, http_code: int, **options) -> None:
        """HTTP responses with errors to the client

        Args:
            http_code (int): HTTP response status code.
        """
        self.http_code = http_code
        for key, value in options.items():
            setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """Convert all attributes to dictionary and exclude http_code of the key.

        Returns:
            All attributes but excluding http_code
        """
        return self.__dict__

    def to_json(self) -> str:
        """Convert all attributes to json and exclude http_code of the key.

        Returns:
            All attributes but excluding http_code
        """
        return json.dumps(self.__dict__)


class ValidationErrorResult(BaseModel):
    loc: list
    type: str
    msg: str
    ctx: Optional[Dict[str, Any]]


class ValidationErrorResponses(BaseModel):
    """No matter how many errors there are, an exception will be raised."""

    results: List[ValidationErrorResult]
