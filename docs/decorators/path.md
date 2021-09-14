## Introduction
You can use path decorator to receive request url path.

## Step
1. Create spec and inherit BaseModel
2. Use path decorator
3. Get path from parameters.path
4. When registering the flask route, add the keyword argument

## Example
```python hl_lines="11 12 21 25 30"
from flask import Flask
from flask.views import MethodView
from pydantic import BaseModel

from flask_restapi import Api, RequestParametersType

app = Flask(__name__)
api = Api(app)


class UserPathSpec(BaseModel):
    name: str


class UserResponseSpec(BaseModel):
    id: int
    name: str


class User(MethodView):
    @api.path(UserPathSpec)
    @api.response(UserResponseSpec)
    def get(self, parameters: RequestParametersType):
        """Get a user name and id"""
        user_name = parameters.path.name
        response = UserResponseSpec(id=1, name=user_name)
        return response.dict()


app.add_url_rule("/user/<string:name>", view_func=User.as_view("user"))
```