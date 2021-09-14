## Introduction
If you don't want to use flask methodview, You can also use decorators in the case of function based view.
!!! Note
    If you want to output spec correctly, you must describe {==endpoint_name==} and {==method_name==} on decorators

## Example
```python hl_lines="25-31"
from flask import Flask
from flask.views import MethodView
from pydantic import BaseModel

from flask_restapi import Api, RequestParameters

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


@app.route("/user")
@api.query(UserGetSpec, endpoint="user_get", method_name="get")
@api.response(UserResponseSpec, endpoint="user_get", method_name="get")
def user_get(parameters: RequestParameters):
    user_name = parameters.query.name
    response = UserResponseSpec(id=1, name=user_name)
    return response.dict()
```
