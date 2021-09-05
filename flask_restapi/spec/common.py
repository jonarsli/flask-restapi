from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


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
