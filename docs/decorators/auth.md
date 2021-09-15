## Introduction
You can use auth decorator to receive authorization token by headers. This auth decorator will get the Authorization of Flask request.headers and mark the endpoint on the spec as requiring verification.
!!! Note
    If Authorization prefix contains "Bearer", it will be automatically removed

## Step
1. Use auth decorator
2. Get token from parameters.auth


## Example
```python hl_lines="21 27"
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
    @api.auth()
    @api.body(UserBodySpec)
    @api.response(UserResponseSpec)
    def post(self, parameters: RequestParametersType):
        """Get a user name and id"""
        user_name = parameters.body.name
        token = parameters.auth
        return UserResponseSpec(id=1, name=user_name)


app.add_url_rule("/user", view_func=User.as_view("user"))
```