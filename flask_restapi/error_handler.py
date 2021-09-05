from pydantic import ValidationError

from .exception import ApiException, ApiExceptionModel
from .response import ErrorResponse


class ErrorHandlerMixin:
    def __init__(self) -> None:
        self._response = ErrorResponse()

    def register_error_handlers(self) -> None:
        self.app.register_error_handler(ApiException, self._handle_api_exception)
        self.app.register_error_handler(ValidationError, self._handle_validation_error)

    def _handle_validation_error(self, error: ValidationError) -> ErrorResponse:
        self._response.status = 422
        self._response.data = ApiExceptionModel(
            http_code=422,
            description=str(error),
            error_code=422,
            error_name="Validation error",
        ).json()
        return self._response

    def _handle_api_exception(self, error: ApiException) -> ErrorResponse:
        self._response.status = error.http_code
        self._response.data = ApiExceptionModel(
            http_code=error.http_code,
            description=error.description,
            error_code=error.error_code or error.http_code,
            error_name=error.error_name or "",
        ).json()
        return self._response
