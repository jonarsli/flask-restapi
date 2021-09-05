from datetime import datetime, timedelta
from typing import Any, Dict

import jwt


class AuthToken:
    def __init__(self, secret_key: str, algorithm: str = "HS256", **subjects) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.subjects = subjects

    def generate(self, expiration_time: timedelta = None) -> str:
        payload = {
            "exp": datetime.utcnow() + (expiration_time or timedelta(days=1)),
            "iat": datetime.utcnow(),
            "sub": self.subjects,
        }
        return jwt.encode(payload, self.secret_key, self.algorithm)

    def verify_token(self, encoded_token: str) -> Dict[str, Any]:
        return jwt.decode(encoded_token, self.secret_key, self.algorithm)
