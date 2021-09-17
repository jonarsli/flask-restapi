# Flask-RESTAPI

[![license](https://img.shields.io/github/license/jonarsli/flask-restapi.svg)](https://github.com/jonarsli/flask-restapi/blob/master/LICENSE)
[![pypi](https://img.shields.io/pypi/v/flask-restapi.svg)](https://pypi.python.org/pypi/flask-restapi)


[Flask-RESTAPI document](https://jonarsli.github.io/flask-restapi/)

Flask-RESTAPI is an extension for Flask that is a database-agnostic framework library for creating REST APIs. It is a lightweight abstraction that works with your existing ORM/libraries.

It use pydantic to validate and serialize data. OpenAPI document can be automatically generated through the python decorator and it supports swagger ui display.

Pydantic are used to validate and serialize parameters. For details, please refer to the [pydantic documentation](https://pydantic-docs.helpmanual.io/).

## Installation
```bash
pip install flask-restapi
```

## Example
```python
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


class User(MethodView):
    @api.query(UserGetSpec)
    @api.response(UserResponseSpec)
    def get(self, parameters: RequestParametersType):
        """Get a user name and id"""
        user_name = parameters.query.name
        return UserResponseSpec(id=1, name=user_name)


app.add_url_rule("/user", view_func=User.as_view("user"))

```

## Swagger API docs
Now go to http://localhost:5000/docs
![](docs/images/example.png)