## Introduction
You can use header decorator to receive request header.
From [RFC 2616 - "Hypertext Transfer Protocol -- HTTP/1.1", Section 4.2, "Message Headers":](https://www.w3.org/Protocols/rfc2616/rfc2616-sec4.html#sec4.2)
> Each header field consists of a name followed by a colon (":") and the field value. Field names are case-insensitive.
!!! Note
    Please use lowercase to spec attribute.

## Step
1. Create spec and inherit BaseModel
2. Use header decorator
3. Get header from parameters.header

## Example
```python hl_lines="11 12 21 25"
from flask import Flask
from flask.views import MethodView
from pydantic import BaseModel

from flask_restapi import Api, RequestParametersType

app = Flask(__name__)
api = Api(app)


class UserHeaderSpec(BaseModel):
    name: str


class UserResponseSpec(BaseModel):
    id: int
    name: str


class User(MethodView):
    @api.header(UserHeaderSpec)
    @api.response(UserResponseSpec)
    def get(self, parameters: RequestParametersType):
        """Get a user name and id"""
        user_name = parameters.header.name
        return UserResponseSpec(id=1, name=user_name)


app.add_url_rule("/user", view_func=User.as_view("user"))
```