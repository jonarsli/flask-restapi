## Introduction
You can use query decorator to receive request query string.


## Step
1. Create spec and inherit BaseModel
2. Use query decorator
3. Get query from parameters.query

## Example
```python hl_lines="11 12 21 25 30"
from flask import Flask
from flask.views import MethodView
from pydantic import BaseModel

from flask_restapi import Api, RequestParametersType

app = Flask(__name__)
api = Api(app)


class UserQuerySpec(BaseModel):
    name: str


class UserResponseSpec(BaseModel):
    id: int
    name: str


class User(MethodView):
    @api.query(UserQuerySpec)
    @api.response(UserResponseSpec)
    def get(self, parameters: RequestParametersType):
        """Get a user name and id"""
        user_name = parameters.query.name
        return UserResponseSpec(id=1, name=user_name)


app.add_url_rule("/user", view_func=User.as_view("user"))
```