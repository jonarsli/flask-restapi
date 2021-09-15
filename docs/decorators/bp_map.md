## Introduction
If you want to use flask blueprint, in order to bind the URL endpoint to the blueprint name, you must add the "bp map" decorator to the class.

## Example
```python hl_lines="1 9 21 31 32"
from flask import Flask, Blueprint
from flask.views import MethodView
from pydantic import BaseModel

from flask_restapi import Api, RequestParametersType

app = Flask(__name__)
api = Api(app)
bp = Blueprint("user", import_name=__name__)


class UserGetSpec(BaseModel):
    name: str


class UserResponseSpec(BaseModel):
    id: int
    name: str


@api.bp_map(bp.name)
class User(MethodView):
    @api.query(UserGetSpec)
    @api.response(UserResponseSpec)
    def get(self, parameters: RequestParametersType):
        """Get a user name and id"""
        user_name = parameters.query.name
        return UserResponseSpec(id=1, name=user_name)


bp.add_url_rule("/user", view_func=User.as_view("user"))
app.register_blueprint(bp)
```