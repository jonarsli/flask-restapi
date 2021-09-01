from flask import json
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from .response import ErrorResponse


class ErrorHandler:
    def __init__(self) -> None:
        self._response = ErrorResponse()

    def register_error_handlers(self) -> None:
        self.app.register_error_handler(HTTPException, self._handle_http_exception)
        self.app.register_error_handler(ValidationError, self._handle_validation_error)

    def _handle_validation_error(self, error: ValidationError) -> ErrorResponse:
        self._response.status = 400
        self._response.data = json.dumps(
            {"code": 400, "status": "Validation error", "description": str(error)}
        )
        return self._response

    def _handle_http_exception(self, error: HTTPException) -> ErrorResponse:
        self._response.status = error.code
        self._response.data = json.dumps(
            {"code": error.code, "name": error.name, "description": error.description}
        )
        return self._response
