import functools
from typing import Any, Generic, Optional, Type, TypeVar

from flask import Flask, current_app, request
from pydantic import BaseModel
from pydantic.generics import GenericModel

from flask_restapi.spec.common import InfoModel

from .blueprint import get_spec, get_swagger_docs, restapi_bp
from .error_handler import ErrorHandler
from .response import JSONResponse
from .spec import Spec, SpecPath, TagModel, UrlMapModel

DataT = TypeVar("DataT")


class RequestParameters(GenericModel, Generic[DataT]):
    path: Optional[DataT]
    query: Optional[DataT]
    body: Optional[DataT]


class Api(ErrorHandler):
    def __init__(self, app: Flask = None, response_to_json: bool = True) -> None:
        super().__init__()
        self._response_to_json = response_to_json
        self._spec = Spec()
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        self.app = app
        if self._response_to_json:
            self.app.response_class = JSONResponse

        self._init_config()
        self.app.before_first_request(self._register_spec)
        self._register_blueprint()
        self.register_error_handlers()

    def path(self, schema: Type[BaseModel], endpoint: str, tag: Type[TagModel] = None):
        def decorator(func):
            self._spec.store_parameters("path", schema, endpoint, func.__name__, tag)

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                request.parameters = self._get_request_parameters()
                request.parameters.path = schema(**request.view_args)
                return func(self, request.parameters)

            return wrapper

        return decorator

    def query(self, schema: Type[BaseModel], endpoint: str, tag: Type[TagModel] = None):
        def decorator(func):
            self._spec.store_parameters("query", schema, endpoint, func.__name__, tag)

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                request.parameters = self._get_request_parameters()
                request.parameters.query = schema(**request.args.to_dict())
                return func(self, request.parameters)

            return wrapper

        return decorator

    def body(
        self,
        schema: Type[BaseModel],
        endpoint: str,
        content_type: list = ["application/json"],
        tag: Type[TagModel] = None,
    ):
        def decorator(func):
            self._spec.store_body(schema, endpoint, func.__name__, content_type, tag)

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                request.parameters = self._get_request_parameters()
                body: Any = request.get_json()
                request.parameters.body = schema(**body)
                return func(self, request.parameters)

            return wrapper

        return decorator

    def response(
        self,
        schema: Type[BaseModel],
        endpoint: str,
        content_type: list = ["application/json"],
        code: int = 200,
    ):
        def decorator(func):
            self._spec.store_responses(
                code, schema, endpoint, func.__name__, content_type
            )

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def _init_config(self):
        self.app.config.setdefault("OPENAPI_VERSION", "3.0.2")
        self.app.config.setdefault("API_TITLE", "Flask RESTAPI")
        self.app.config.setdefault("API_VERSION", "0.1.0")
        self.app.config.setdefault("SPEC_URL", "/api/spec.json")
        self.app.config.setdefault("SWAGGER_UI_URL", "/docs")

    def _get_request_parameters(self) -> RequestParameters:
        if not hasattr(request, "parameters"):
            request.parameters = RequestParameters()

        return request.parameters

    def _register_spec(self) -> None:
        for url_map in self.app.url_map.iter_rules():
            self._spec.url_maps.append(
                UrlMapModel(url=url_map.rule, endpoint=url_map.endpoint)
            )

        for url_map in self._spec.url_maps:
            for endpoint_map in self._spec.endpoint_maps:
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
                    if Spec.spec_model.paths.get(spec_path.url):
                        Spec.spec_model.paths[spec_path.url].update(_paths)
                    else:
                        Spec.spec_model.paths.update({spec_path.url: _paths})
        Spec.spec_model.openapi = current_app.config["OPENAPI_VERSION"]
        Spec.spec_model.info = InfoModel(
            title=current_app.config["API_TITLE"],
            version=current_app.config["API_VERSION"],
        )
        Spec.spec_model.components = self._spec.components
        Spec.spec_model.tags = self._spec.tags

    def _register_blueprint(self):
        with self.app.app_context():
            restapi_bp.add_url_rule(current_app.config["SPEC_URL"], view_func=get_spec)
            restapi_bp.add_url_rule(
                current_app.config["SWAGGER_UI_URL"], view_func=get_swagger_docs
            )
        self.app.register_blueprint(restapi_bp)
