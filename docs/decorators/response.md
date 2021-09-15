## Introduction
You can use response decorator to make response schema to spec document. If you need multiple response specification documents, you can use multiple response decorators to achieve.

!!! Note
    If it detects that the return type is Pydantic BaseModel, it will be automatically converted to dictionary.

## Step
1. Create spec and inherit BaseModel
2. Use response decorator
3. Return response

```python hl_lines="16 17 18 21 22 27 28 35"
from flask import Flask
from flask.views import MethodView
from pydantic import BaseModel

from flask_restapi import Api, RequestParametersType, ApiException

app = Flask(__name__)
api = Api(app)


class UserCreateSpec(BaseModel):
    name: str
    password: str


class UserResponseSpec(BaseModel):
    id: int
    name: str


class UserAuthErrorSepc(BaseModel):
    description: str


class User(MethodView):
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