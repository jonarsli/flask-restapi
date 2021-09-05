import functools
from typing import Any, Generic, Optional, Type, TypeVar

from flask import Flask, current_app, request
from pydantic import BaseModel
from pydantic.generics import GenericModel

from .error_handler import ErrorHandlerMixin
from .response import JSONResponse
from .spec import BlueprintMap, InfoModel, SpecPath, TagModel, UrlMapModel, spec
from .view import get_spec, get_swagger_docs, restapi_bp

DataT = TypeVar("DataT")


class RequestParameters(GenericModel, Generic[DataT]):
    path: Optional[DataT]
    query: Optional[DataT]
    body: Optional[DataT]
    token: Optional[str]


class Api(ErrorHandlerMixin):
    def __init__(self, app: Flask = None, response_to_json: bool = True) -> None:
        super().__init__()
        self._response_to_json = response_to_json
        self.spec = spec
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

    def bp_map(self, blueprint_name: str = None, endpoint_name: str = None):
        def decorator(cls):
            blueprint_map = BlueprintMap(
                endpoint_name=endpoint_name or cls.__name__.lower(),
                blueprint_name=blueprint_name,
            )
            self.spec.blueprint_maps.append(blueprint_map)

            return cls

        return decorator

    def path(
        self,
        schema: Type[BaseModel],
        endpoint: str = None,
        tag: Type[TagModel] = None,
    ):
        def decorator(func):
            ep = endpoint if endpoint else self._generate_endpoint(func.__qualname__)
            self.spec.store_parameters("path", schema, ep, func.__name__, tag)

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                request.parameters = self._get_request_parameters()
                request.parameters.path = schema(**request.view_args)
                return func(self, request.parameters)

            return wrapper

        return decorator

    def query(
        self,
        schema: Type[BaseModel],
        endpoint: str = None,
        tag: Type[TagModel] = None,
    ):
        def decorator(func):
            ep = endpoint if endpoint else self._generate_endpoint(func.__qualname__)
            self.spec.store_parameters("query", schema, ep, func.__name__, tag)

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
        endpoint: str = None,
        content_type: list = ["application/json"],
        tag: Type[TagModel] = None,
    ):
        def decorator(func):
            ep = endpoint if endpoint else self._generate_endpoint(func.__qualname__)
            self.spec.store_body(schema, ep, func.__name__, content_type, tag)

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                request.parameters = self._get_request_parameters()
                body: Any = request.get_json()
                request.parameters.body = schema(**body)
                return func(self, request.parameters)

            return wrapper

        return decorator

    def auth(self, endpoint: str = None):
        def decorator(func):
            ep = endpoint if endpoint else self._generate_endpoint(func.__qualname__)
            self.spec.store_auth(ep, func.__name__)

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                request.parameters = self._get_request_parameters()
                auth_header = request.headers.get("Authorization")
                if " " in auth_header:
                    request.parameters.token = auth_header.split(" ")[1]

                return func(self, request.parameters)

            return wrapper

        return decorator

    def response(
        self,
        schema: Type[BaseModel],
        endpoint: str = None,
        content_type: list = ["application/json"],
        code: int = 200,
    ):
        def decorator(func):
            ep = endpoint if endpoint else self._generate_endpoint(func.__qualname__)
            self.spec.store_responses(code, schema, ep, func.__name__, content_type)

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(self, request.parameters)

            return wrapper

        return decorator

    def _init_config(self):
        self.app.config.setdefault("OPENAPI_VERSION", "3.0.2")
        self.app.config.setdefault("API_TITLE", "Flask RESTAPI")
        self.app.config.setdefault("API_VERSION", "0.1.0")
        self.app.config.setdefault("SPEC_URL", "/api/spec.json")
        self.app.config.setdefault("SWAGGER_UI_URL", "/docs")
        self.app.config.setdefault("RESTAPI_SECRET_KEY", "FlaskRESTAPIKey")

    def _get_request_parameters(self) -> RequestParameters:
        if not hasattr(request, "parameters"):
            request.parameters = RequestParameters()

        return request.parameters

    def _generate_endpoint(self, endpoint: str) -> str:
        return endpoint.split(".")[0].lower()

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
