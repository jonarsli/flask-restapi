## Introduction
If you don't want to use flask methodview, You can also use decorators in the case of function based view.
!!! Note
    If you want to output spec correctly, you must describe {==endpoint_name==} and {==method_name==} on decorators

## Example

=== "General"
    ```python hl_lines="24-29"
    from flask import Flask
    from pydantic import BaseModel

    from flask_restapi import Api, RequestParametersType

    app = Flask(__name__)
    api = Api(app)


    class UserGetSpec(BaseModel):
        name: str


    class UserCreateSpec(BaseModel):
        name: str
        password: str


    class UserResponseSpec(BaseModel):
        id: int
        name: str


    @app.route("/user")
    @api.query(UserGetSpec, endpoint="user_get", method_name="get")
    @api.response(UserResponseSpec, endpoint="user_get", method_name="get")
    def user_get(self, parameters: RequestParametersType):
        user_name = parameters.query.name
        return UserResponseSpec(id=1, name=user_name)

    ```

=== "Blueprint"
    ```python hl_lines="1 8 26 34"
    from flask import Flask, Blueprint
    from pydantic import BaseModel

    from flask_restapi import Api, RequestParametersType

    app = Flask(__name__)
    api = Api(app)
    bp = Blueprint("user", import_name=__name__)


    class UserGetSpec(BaseModel):
        name: str


    class UserCreateSpec(BaseModel):
        name: str
        password: str


    class UserResponseSpec(BaseModel):
        id: int
        name: str


    @bp.route("/user")
    @api.bp_map(bp.name)
    @api.query(UserGetSpec, endpoint="user_get", method_name="get")
    @api.response(UserResponseSpec, endpoint="user_get", method_name="get")
    def user_get(self, parameters: RequestParametersType):
        user_name = parameters.query.name
        return UserResponseSpec(id=1, name=user_name)


    app.register_blueprint(bp)
    ```