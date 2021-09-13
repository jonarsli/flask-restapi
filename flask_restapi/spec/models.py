import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class ExternalDocs(BaseModel):
    description: str
    url: str


class TagModel(BaseModel):
    name: str
    description: str
    external_Docs: Optional[ExternalDocs]


class SpecComponents(BaseModel):
    schemas: Optional[Dict[str, Any]]
    securitySchemes: Optional[Dict[str, Any]]


class InfoModel(BaseModel):
    title: str
    version: str


class CommonRef(BaseModel):
    api_ref: str = Field(alias="$ref")

    class Config:
        allow_population_by_field_name = True


class CommonSchema(BaseModel):
    api_schema: CommonRef = Field(alias="schema")

    class Config:
        allow_population_by_field_name = True


class CommonContent(BaseModel):
    description: Optional[str]
    content: Dict[str, CommonSchema]


class UrlMapModel(BaseModel):
    url: str
    endpoint: str

    @validator("url")
    def convert(cls, value):
        original_rules = re.findall("<.*?>", value)
        for rule in original_rules:
            rule_splits = rule.split(":")
            if len(rule_splits) == 2:
                converted_rule = "{" + rule_splits[1][:-1] + "}"
            else:
                converted_rule = "{" + rule_splits[0][1:-1] + "}"

            value = value.replace(rule, converted_rule)

        return value


class ParameterModel(BaseModel):
    name: str
    location: str = Field(alias="in")
    required: bool
    api_schema: dict = Field(alias="schema")
    description: Optional[str]

    class Config:
        allow_population_by_field_name = True


class RequestBodyModel(BaseModel):
    content: Dict[str, CommonSchema]
    required: bool = True
    description: Optional[str]


class EndPointModel(BaseModel):
    summary: Optional[str]
    description: Optional[str]
    operationId: Optional[str]
    parameters: Optional[List[ParameterModel]]
    requestBody: Optional[RequestBodyModel]
    responses: Optional[Dict[str, CommonContent]]
    tags: Optional[List[str]]
    security: Optional[List[Dict[str, Any]]]


class BlueprintMap(BaseModel):
    endpoint_name: str
    blueprint_name: Optional[str]


class EndPointMap(BaseModel):
    endpoint_name: str
    method_name: Optional[str]
    model: EndPointModel


class SpecPath(BaseModel):
    url: str
    method_name: str
    endpoint_model: EndPointModel
