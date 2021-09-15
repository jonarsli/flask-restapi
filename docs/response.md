## Handling error
To return HTTP responses with errors to the client you use `ApiException`.

!!! Note
    If you don’t want to add additional error specs to spec.json, you can not use response decorators for error responses.

```python hl_lines="5 39 44"
from flask import Flask
from flask.views import MethodView
from pydantic import BaseModel

from flask_restapi import Api, RequestParametersType, ApiException

app = Flask(__name__)
api = Api(app)


class UserGetSpec(BaseModel):
    name: str


class UserCreateSpec(BaseModel):
    name: str
    password: str


class UserResponseSpec(BaseModel):
    id: int
    name: str


class UserAuthErrorSepc(BaseModel):
    description: str


class User(MethodView):
    @api.query(UserGetSpec)
    @api.response(UserResponseSpec)
    def get(self, parameters: RequestParametersType):
        """Get a user name and id"""
        user_name = parameters.query.name
        return UserResponseSpec(id=1, name=user_name)

    @api.body(UserCreateSpec)
    @api.response(UserResponseSpec)
    @api.response(UserAuthErrorSepc, code=401)
    def post(self, parameters: RequestParametersType):
        user_name = parameters.body.name
        user_password = parameters.body.password
        if user_password != "hello":
            raise ApiException(401, description="Password is  incorrect")
        return UserResponseSpec(id=1, name=user_name)


app.add_url_rule("/user", view_func=User.as_view("user"))
```

## Add response header
f you want to add a fixed header to the response, you can add it through the parameter `headers` of the response decorator. However, if you want to dynamically add response headers, you can add `extra = allow` to the response spec config.

```python hl_lines="19 20 25 29 30"
from flask import Flask
from flask.views import MethodView
from pydantic import BaseModel

from flask_restapi import Api, RequestParametersType

app = Flask(__name__)
api = Api(app)


class UserGetSpec(BaseModel):
    name: str


class UserResponseSpec(BaseModel):
    id: int
    name: str

    class Config:
        extra = "allow"


class User(MethodView):
    @api.query(UserGetSpec)
    @api.response(UserResponseSpec, headers={"fix-header": "is fix header"})
    def get(self, parameters: RequestParametersType):
        """Get a user name and id"""
        user_name = parameters.query.name
        headers = {"dynamic-header": "is dynamic header"}
        return UserResponseSpec(id=1, name=user_name, headers=headers)


app.add_url_rule("/user", view_func=User.as_view("user"))

```