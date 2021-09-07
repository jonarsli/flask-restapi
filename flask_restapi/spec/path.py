import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from .common import CommonContent, CommonSchema


class UrlMapModel(BaseModel):
    url: str
    endpoint: str

    @validator("url")
    def convert(cls, value):
        original_rules = re.findall("<.*?>", value)
        for rule in original_rules:
            rule_splits = rule.split(":")
            converted_rule = "{" + rule_splits[1][:-1] + "}"
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
