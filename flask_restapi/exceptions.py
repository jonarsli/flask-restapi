import json
from typing import Any, Dict


class ApiException(Exception):
    def __init__(self, http_code: int, **options) -> None:
        self.http_code = http_code
        for key, value in options.items():
            setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

    def to_json(self) -> str:
        return json.dumps(self.__dict__)
