import functools
from typing import Any, Generic, Optional, Type, TypeVar

from flask import Flask, request
from pydantic import BaseModel
from pydantic.generics import GenericModel

from .mixin import AuthTokenMixin, ErrorHandlerMixin, SpecMixin
from .response import JSONResponse
from .spec import BlueprintMap, TagModel

DataT = TypeVar("DataT")


class RequestParameters(GenericModel, Generic[DataT]):
    path: Optional[DataT]
    query: Optional[DataT]
    body: Optional[DataT]
    token: Optional[str]


class Api(SpecMixin, AuthTokenMixin, ErrorHandlerMixin):
    def __init__(self, app: Flask = None, algorithm: str = "HS256") -> None:
        SpecMixin.__init__(self)
        AuthTokenMixin.__init__(self, algorithm)
        ErrorHandlerMixin.__init__(self)
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        self.app = app
        self.app.response_class = JSONResponse

        SpecMixin._init_config(self)
        AuthTokenMixin._init_config(self)

        self.app.before_first_request(self._register_spec)
        self._register_blueprint()
        self._register_error_handlers()

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
        summary: str = None,
    ):
        def decorator(func):
            ep = endpoint if endpoint else self._generate_endpoint(func.__qualname__)
            _summary = summary or func.__doc__ or None
            self.spec.store_parameters("path", schema, ep, func.__name__, tag, _summary)

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
        summary: str = None,
    ):
        def decorator(func):
            ep = endpoint if endpoint else self._generate_endpoint(func.__qualname__)
            _summary = summary or func.__doc__ or None
            self.spec.store_parameters(
                "query", schema, ep, func.__name__, tag, _summary
            )

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
        summary: str = None,
    ):
        def decorator(func):
            ep = endpoint if endpoint else self._generate_endpoint(func.__qualname__)
            _summary = summary or func.__doc__ or None
            self.spec.store_body(schema, ep, func.__name__, content_type, tag, _summary)

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
                if auth_header is not None:
                    if "Bearer" in auth_header:
                        _token = auth_header.split(" ")[1]
                        request.parameters.token = _token

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
                request.parameters = self._get_request_parameters()
                return func(self, request.parameters)

            return wrapper

        return decorator

    def add_component_to_docs(self, schema: Type[BaseModel]):
        def decorator(func):
            self.spec._store_components(schema)

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                request.parameters = self._get_request_parameters()
                return func(self, request.parameters)

            return wrapper

        return decorator

    def _get_request_parameters(self) -> RequestParameters:
        if not hasattr(request, "parameters"):
            request.parameters = RequestParameters()

        return request.parameters

    def _generate_endpoint(self, endpoint: str) -> str:
        return endpoint.split(".")[0].lower()
