## Introduction
You can use body decorator to receive request body.
!!! Note
    content-type: application/json

## Step
1. Create spec and inherit BaseModel
2. Use body decorator
3. Get body from parameters.body

## Example
```python hl_lines="11 12 21 25"
from flask import Flask
from flask.views import MethodView
from pydantic import BaseModel

from flask_restapi import Api, RequestParametersType

app = Flask(__name__)
api = Api(app)


class UserBodySpec(BaseModel):
    name: str


class UserResponseSpec(BaseModel):
    id: int
    name: str


class User(MethodView):
    @api.body(UserBodySpec)
    @api.response(UserResponseSpec)
    def post(self, parameters: RequestParametersType):
        """Get a user name and id"""
        user_name = parameters.body.name
        return UserResponseSpec(id=1, name=user_name)


app.add_url_rule("/user", view_func=User.as_view("user"))
```