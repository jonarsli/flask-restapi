from datetime import datetime, timedelta
from typing import Any, Dict

from flask import current_app
import jwt


class AuthTokenMixin:
    def __init__(self, algorithm: str = "HS256") -> None:
        self.algorithm = algorithm

    def init_config(self):
        self.app.config.setdefault("RESTAPI_SECRET_KEY", "FlaskRESTAPIKey")

    def encode_token(self, expiration_time: timedelta = None, **subjects) -> str:
        payload = {
            "exp": datetime.utcnow() + (expiration_time or timedelta(days=1)),
            "iat": datetime.utcnow(),
            "sub": subjects,
        }
        return jwt.encode(
            payload, current_app.config["RESTAPI_SECRET_KEY"], self.algorithm
        )

    def decode_token(self, encoded_token: str) -> Dict[str, Any]:
        return jwt.decode(
            encoded_token, current_app.config["RESTAPI_SECRET_KEY"], self.algorithm
        )
