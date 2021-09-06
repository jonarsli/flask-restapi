from datetime import datetime, timedelta
from typing import Any, Dict

import jwt
from flask import current_app
from pydantic import ValidationError

from .exception import ApiException, ApiExceptionModel
from .response import ErrorResponse
from .spec import InfoModel, SpecPath, UrlMapModel, spec
from .view import get_spec, get_swagger_docs, restapi_bp


class SpecMixin:
    def __init__(self) -> None:
        self.spec = spec

    def _init_config(self):
        self.app.config.setdefault("OPENAPI_VERSION", "3.0.2")
        self.app.config.setdefault("API_TITLE", "Flask RESTAPI")
        self.app.config.setdefault("API_VERSION", "0.1.0")
        self.app.config.setdefault("SPEC_URL", "/api/spec.json")
        self.app.config.setdefault("SWAGGER_UI_URL", "/docs")

    def _register_spec(self) -> None:
        for url_map in self.app.url_map.iter_rules():
            self.spec.url_maps.append(
                UrlMapModel(url=url_map.rule, endpoint=url_map.endpoint)
            )

        for blueprint_map in self.spec.blueprint_maps:
            for index, endpoint_map in enumerate(self.spec.endpoint_maps):
                if endpoint_map.endpoint_name == blueprint_map.endpoint_name:
                    self.spec.endpoint_maps[
                        index
                    ].endpoint_name = (
                        f"{blueprint_map.blueprint_name}.{endpoint_map.endpoint_name}"
                    )

        for url_map in self.spec.url_maps:
            for endpoint_map in self.spec.endpoint_maps:
                if url_map.endpoint == endpoint_map.endpoint_name:
                    spec_path = SpecPath(
                        url=url_map.url,
                        method_name=endpoint_map.method_name,
                        endpoint_model=endpoint_map.model,
                    )
                    _paths = {
                        spec_path.method_name: spec_path.endpoint_model.dict(
                            by_alias=True, exclude_none=True, exclude={"method_name"}
                        )
                    }
                    if self.spec.spec_model.paths.get(spec_path.url):
                        self.spec.spec_model.paths[spec_path.url].update(_paths)
                    else:
                        self.spec.spec_model.paths.update({spec_path.url: _paths})

        self.spec.spec_model.openapi = current_app.config["OPENAPI_VERSION"]
        self.spec.spec_model.info = InfoModel(
            title=current_app.config["API_TITLE"],
            version=current_app.config["API_VERSION"],
        )
        self.spec.spec_model.components = self.spec.components
        self.spec.spec_model.tags = self.spec.tags

    def _register_blueprint(self):
        with self.app.app_context():
            restapi_bp.add_url_rule(current_app.config["SPEC_URL"], view_func=get_spec)
            restapi_bp.add_url_rule(
                current_app.config["SWAGGER_UI_URL"], view_func=get_swagger_docs
            )
        self.app.register_blueprint(restapi_bp)


class AuthTokenMixin:
    def __init__(self, algorithm: str = "HS256") -> None:
        self.algorithm = algorithm

    def _init_config(self):
        self.app.config.setdefault("RESTAPI_SECRET_KEY", "FlaskRESTAPIKey")

    def encode_token(self, expiration_time: timedelta = None, **subjects) -> str:
        payload = {
            "exp": datetime.utcnow() + (expiration_time or timedelta(days=1)),
            "iat": datetime.utcnow(),
            "sub": subjects,
        }
        return jwt.encode(
            payload, current_app.config["RESTAPI_SECRET_KEY"], self.algorithm
        )

    def decode_token(self, encoded_token: str) -> Dict[str, Any]:
        return jwt.decode(
            encoded_token, current_app.config["RESTAPI_SECRET_KEY"], self.algorithm
        )


class ErrorHandlerMixin:
    def __init__(self) -> None:
        self._response = ErrorResponse()

    def _register_error_handlers(self) -> None:
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
