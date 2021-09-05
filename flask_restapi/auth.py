from datetime import datetime, timedelta
from typing import Any, Dict

from flask import Flask, current_app
import jwt


class AuthToken:
    def __init__(self, app: Flask = None, algorithm: str = "HS256") -> None:
        self.app = app
        self.algorithm = algorithm
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        self.app = app
        self.app.config.setdefault("RESTAPI_SECRET_KEY", "FlaskRESTAPIKey")

    def generate(self, expiration_time: timedelta = None, **subjects) -> str:
        payload = {
            "exp": datetime.utcnow() + (expiration_time or timedelta(days=1)),
            "iat": datetime.utcnow(),
            "sub": subjects,
        }
        return jwt.encode(
            payload, current_app.config["RESTAPI_SECRET_KEY"], self.algorithm
        )

    def verify_token(self, encoded_token: str) -> Dict[str, Any]:
        return jwt.decode(
            encoded_token, current_app.config["RESTAPI_SECRET_KEY"], self.algorithm
        )
