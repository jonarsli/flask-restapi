## Introduction
Flask-REST API auth is a thin integration of PyJWT. Implemented an auth decorator to pass token. And include Encode, Decode function.
!!! Note
    For the usage of auth decorator, please refer to

## Example
```python hl_lines="45 52 58 61 64-66"
from flask import Flask
from flask.views import MethodView
from pydantic import BaseModel

from flask_restapi import Api, RequestParametersType, ApiException

app = Flask(__name__)
api = Api(app)


class UserGetSpec(BaseModel):
    pass


class UserGetResponseSpec(BaseModel):
    id: str
    name: str


class UserLoginSpec(BaseModel):
    name: str
    password: str


class UserLoginResponseSpec(BaseModel):
    token: str


class UserAuthErrorResponseSpec(BaseModel):
    http_code: int
    description: str


class User(MethodView):
    @api.body(UserLoginSpec)
    @api.response(UserLoginResponseSpec)
    @api.response(UserAuthErrorResponseSpec, code=401)
    def post(self, parameters: RequestParametersType):
        """User login"""
        # You can verify username and password
        user_name = parameters.body.name
        user_password = parameters.body.password
        if user_name == "admin" and user_password == "hello":
            # Encode token
            token = api.encode_token(username=user_name)

            response = UserLoginResponseSpec(token=token)
            return response.dict()
        else:
            raise ApiException(401, description="Username or password incorrect")

    @api.auth()
    @api.query(UserGetSpec)
    @api.response(UserGetResponseSpec)
    def get(self, parameters: RequestParametersType):
        """Get user name and id"""
        # You can get token from parameters.auth
        token = parameters.auth

        # Decode token to payload
        payload = api.decode_token(token)

        # Payload include "Expiration Time", "Issued At", "Subject"
        exp = payload["exp"]
        iat = payload["iat"]
        sub = payload["sub"]

        # You can verify payload info
        if sub["username"] == "admin":
            response = UserGetResponseSpec(id=1, name="admin")

        return response.dict()


app.add_url_rule("/user", view_func=User.as_view("user"))
```