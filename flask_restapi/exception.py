from typing import Optional

from pydantic import BaseModel


class ApiExceptionModel(BaseModel):
    http_code: int
    description: str
    error_code: Optional[int]
    error_name: Optional[str]


class ApiException(Exception):
    def __init__(
        self,
        http_code: int,
        description: str,
        error_code: int = None,
        error_name: str = None,
    ) -> None:
        self.http_code = http_code
        self.description = description
        self.error_code = error_code
        self.error_name = error_name
