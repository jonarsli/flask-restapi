## Introduction
Decorators (path, query, title, body, form) have `tag` parameters, which can be used to distinguish API operations.

## Example
```python hl_lines="5 21"
from flask import Flask
from flask.views import MethodView
from pydantic import BaseModel

from flask_restapi import Api, RequestParametersType, TagModel

app = Flask(__name__)
api = Api(app)


class UserGetSpec(BaseModel):
    name: str


class UserResponseSpec(BaseModel):
    id: int
    name: str


class User(MethodView):
    @api.query(UserGetSpec, tag=TagModel(name="user", description="User tag"))
    @api.response(UserResponseSpec)
    def get(self, parameters: RequestParametersType):
        """Get a user name and id"""
        user_name = parameters.query.name
        return UserResponseSpec(id=1, name=user_name)


app.add_url_rule("/user", view_func=User.as_view("user"))
```
