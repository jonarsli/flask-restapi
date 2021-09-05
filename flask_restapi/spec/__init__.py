from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel

from .common import (
    CommonContent,
    CommonRef,
    CommonSchema,
    InfoModel,
    SpecComponents,
    TagModel,
)
from .path import (  # noqa: F401
    BlueprintMap,
    EndPointMap,
    EndPointModel,
    ParameterModel,
    RequestBodyModel,
    SpecPath,
    UrlMapModel,
)


class SpecModel(BaseModel):
    openapi: Optional[str]
    info: Optional[InfoModel]
    paths: Optional[Dict[str, Any]]
    components: Optional[SpecComponents]
    tags: Optional[List[TagModel]]


class Spec:
    def __init__(self) -> None:
        self.url_maps: List[UrlMapModel] = []
        self.blueprint_maps: List[BlueprintMap] = []
        self.endpoint_maps: List[EndPointMap] = []
        self.components = SpecComponents(schemas={})
        self.tags: List[TagModel] = []
        self.spec_model = SpecModel(paths={})

    def store_parameters(
        self,
        location: str,
        schema: Type[BaseModel],
        endpoint_name: str,
        method_name: str,
        tag: TagModel = None,
    ) -> None:
        schema_dict = schema.schema()
        parameters: List[ParameterModel] = []
        for key, value in schema_dict["properties"].items():
            parameter = ParameterModel(
                name=key,
                location=location,
                required=True if key in schema_dict["required"] else False,
                api_schema=value,
            )
            parameters.append(parameter)

        self._inject_endpoint(
            endpoint_name, method_name, parameters=parameters, tag=tag
        )

    def store_body(
        self,
        schema: Type[BaseModel],
        endpoint_name: str,
        method_name: str,
        content_type: list,
        tag: TagModel = None,
    ):
        self._store_components(schema)
        schema_dict = schema.schema()
        description = schema_dict.get("description") or "No description"
        common_ref = CommonRef(api_ref=f"#/components/schemas/{schema_dict['title']}")
        common_schema = CommonSchema(api_schema=common_ref)
        content = {}
        for ct in content_type:
            content.update({ct: common_schema})

        request_body = RequestBodyModel(description=description, content=content)

        self._inject_endpoint(
            endpoint_name, method_name, request_body=request_body, tag=tag
        )

    def store_auth(self, endpoint_name: str, method_name: str) -> None:
        if not self.components.securitySchemes:
            self.components.securitySchemes = {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            }
        security = [{"bearerAuth": []}]
        self._inject_endpoint(endpoint_name, method_name, security=security)

    def store_responses(
        self,
        code: int,
        schema: Type[BaseModel],
        endpoint_name: str,
        method_name: str,
        content_type: list,
    ):
        self._store_components(schema)
        schema_dict = schema.schema()
        description = schema_dict.get("description") or "No description"
        common_ref = CommonRef(api_ref=f"#/components/schemas/{schema_dict['title']}")
        common_schema = CommonSchema(api_schema=common_ref)
        content = {}
        for ct in content_type:
            content.update({ct: common_schema})

        common_content = CommonContent(description=description, content=content)
        responses = {str(code): common_content}

        self._inject_endpoint(endpoint_name, method_name, responses=responses)

    def _store_components(self, schema: Type[BaseModel]) -> None:
        schema_dict = schema.schema()
        self.components.schemas.update({schema_dict["title"]: schema_dict})

    def _store_tags(self, tag: TagModel) -> None:
        if self.tags:
            for _tag in self.tags:
                if tag.name == _tag.name:
                    break
            else:
                self.tags.append(tag)
        else:
            self.tags.append(tag)

    def _inject_endpoint(
        self,
        endpoint_name: str,
        method_name: str,
        parameters: List[ParameterModel] = None,
        request_body: RequestBodyModel = None,
        responses: Dict[str, Any] = None,
        tag: TagModel = None,
        security: List[dict] = None,
    ):
        for index, em in enumerate(self.endpoint_maps):
            if endpoint_name == em.endpoint_name and method_name == em.method_name:
                if isinstance(parameters, list):
                    if isinstance(em.model.parameters, list):
                        em.model.parameters += parameters
                    else:
                        em.model.parameters = parameters

                if isinstance(responses, dict):
                    if isinstance(em.model.responses, dict):
                        em.model.responses.update(responses)
                    else:
                        em.model.responses = responses

                if isinstance(request_body, RequestBodyModel):
                    em.model.requestBody = request_body

                if isinstance(tag, TagModel):
                    self._store_tags(tag)
                    if not em.model.tags:
                        em.model.tags = []
                    if tag.name not in em.model.tags:
                        em.model.tags.append(tag.name)

                if isinstance(security, list):
                    em.model.security = security

                self.endpoint_maps[index] = em
                break
        else:
            endpoint_map = EndPointMap(
                endpoint_name=endpoint_name,
                method_name=method_name,
                model=EndPointModel(
                    parameters=parameters,
                    request_body=request_body,
                    responses=responses,
                    tags=tag,
                    security=security,
                ),
            )
            self.endpoint_maps.append(endpoint_map)


spec = Spec()
