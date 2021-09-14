## Introduction
You can use form decorator to receive request form data.
!!! Note
    content-type: multipart/form-data

## Step
1. Create spec and inherit BaseModel
2. Use form decorator
3. Get form from parameters.form

## Example
```python hl_lines="11 12 21 25"
from flask import Flask
from flask.views import MethodView
from pydantic import BaseModel

from flask_restapi import Api, RequestParametersType

app = Flask(__name__)
api = Api(app)


class UserFormSpec(BaseModel):
    name: str


class UserResponseSpec(BaseModel):
    id: int
    name: str


class User(MethodView):
    @api.form(UserFormSpec)
    @api.response(UserResponseSpec)
    def post(self, parameters: RequestParametersType):
        """Get a user name and id"""
        user_name = parameters.form.name
        response = UserResponseSpec(id=1, name=user_name)
        return response.dict()


app.add_url_rule("/user", view_func=User.as_view("user"))
```