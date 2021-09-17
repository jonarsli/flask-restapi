## Introduction
Form Decorator support upload files.
!!! Note
    Parameters will store the type of `werkzeug.FileStorage`.

## Example

```python hl_lines="5 13 22 27 28"
from flask import Flask
from flask.views import MethodView
from pydantic import BaseModel

from flask_restapi import Api, RequestParametersType, FileStorageType

app = Flask(__name__)
api = Api(app)


class UserFormSpec(BaseModel):
    name: str
    image: FileStorageType


class UserResponseSpec(BaseModel):
    id: int
    name: str


class User(MethodView):
    @api.form(UserFormSpec)
    @api.response(UserResponseSpec)
    def post(self, parameters: RequestParametersType):
        """Post a user name and image"""
        user_name = parameters.form.name
        image = parameters.form.image
        image.save("Myimage.png")
        return UserResponseSpec(id=1, name=user_name)


app.add_url_rule("/user", view_func=User.as_view("user"))
```