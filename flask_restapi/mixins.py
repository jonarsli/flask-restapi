from typing import Any, Dict

from flask import Blueprint, Response, current_app, render_template
from flask.helpers import make_response
from pydantic import ValidationError

from .exceptions import ApiException, ValidationErrorResponses
from .spec import spec
from .spec.models import InfoModel, SpecPath, UrlMapModel


class SpecMixin:
    def __init__(self) -> None:
        self.spec = spec

    def _init_config(self) -> None:
        self.app.config.setdefault("OPENAPI_VERSION", "3.0.2")
        self.app.config.setdefault("API_TITLE", "Flask RESTAPI")
        self.app.config.setdefault("API_VERSION", "0.1.0")
        self.app.config.setdefault("SPEC_URL", "/api/spec.json")
        self.app.config.setdefault("SWAGGER_UI_URL", "/docs")

    def _register_spec(self) -> None:
        # Add url rules and endpoint to url_maps.
        for url_map in self.app.url_map.iter_rules():
            self.spec.url_maps.append(
                UrlMapModel(url=url_map.rule, endpoint=url_map.endpoint)
            )

        # Mapping blueprint_map, endpoint_map in name,
        # and override endpoint_map name.
        for blueprint_map in self.spec.blueprint_maps:
            for index, endpoint_map in enumerate(self.spec.endpoint_maps):
                if endpoint_map.endpoint_name == blueprint_map.endpoint_name:
                    self.spec.endpoint_maps[
                        index
                    ].endpoint_name = (
                        f"{blueprint_map.blueprint_name}.{endpoint_map.endpoint_name}"
                    )

        # Mapping url_map.endpoint, endpoint_map.endpoint_name,
        # and register endpoint_map to spec document.
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

        # Register openapi, info, components, tags to spec document.
        self.spec.spec_model.openapi = current_app.config["OPENAPI_VERSION"]
        self.spec.spec_model.info = InfoModel(
            title=current_app.config["API_TITLE"],
            version=current_app.config["API_VERSION"],
        )
        self.spec.spec_model.components = self.spec.components
        self.spec.spec_model.tags = self.spec.tags

    def _get_spec(self) -> Dict[str, Any]:
        return spec.spec_model.dict(exclude_none=True)

    def _get_swagger_docs(self) -> str:
        return render_template("swagger_ui.html")

    def _register_blueprint(self) -> None:
        restapi_bp = Blueprint("restapi", __name__, template_folder="templates")
        with self.app.app_context():
            restapi_bp.add_url_rule(
                current_app.config["SPEC_URL"], view_func=self._get_spec
            )
            restapi_bp.add_url_rule(
                current_app.config["SWAGGER_UI_URL"], view_func=self._get_swagger_docs
            )
        self.app.register_blueprint(restapi_bp)


class HandlerMixin:
    def __init__(self) -> None:
        pass

    def _register_handlers(self) -> None:
        self.app.register_error_handler(ApiException, self._handle_api_exception)
        self.app.register_error_handler(ValidationError, self._handle_validation_error)

    def _handle_validation_error(self, error: ValidationError) -> Response:
        return make_response(
            ValidationErrorResponses(results=error.errors()).dict(), 422
        )

    def _handle_api_exception(self, error: ApiException) -> Response:
        return make_response(error.to_dict(), error.http_code)
