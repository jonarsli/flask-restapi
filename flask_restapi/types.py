from typing import Generic, Optional, TypeVar

from pydantic.generics import GenericModel
from werkzeug.datastructures import FileStorage

DataT = TypeVar("DataT")


class FileStorageType(bytes):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, FileStorage):
            raise TypeError("FileStorage required")
        return v

    def __repr__(self):
        return f"FilesType({super().__repr__()})"


class RequestParametersType(GenericModel, Generic[DataT]):
    path: Optional[DataT]
    query: Optional[DataT]
    body: Optional[DataT]
    header: Optional[DataT]
    form: Optional[DataT]
    auth: Optional[str]
