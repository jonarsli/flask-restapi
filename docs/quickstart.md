## Initializing Extensions

Initialize flask and api instance

```python hl_lines="3 6"
from flask import Flask

from flask_restapi import Api

app = Flask(__name__)
api = Api(app)
```
## Create sepc model

Create parameter and response for spec model.

```python hl_lines="10 11 14-16 19-21"

from flask import Flask
from pydantic import BaseModel

from flask_restapi import Api

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
```

## Create flask view

Create flask MethodView and add route url to flask.
Although it can be used without MethodView, but is not recommended.

```python hl_lines="25 28 35"
from flask import Flask
from flask.views import MethodView
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


class User(MethodView):
    @api.query(UserGetSpec)
    @api.response(UserResponseSpec)
    def get(self, parameters: RequestParametersType):
        """Get a user name and id"""
        user_name = parameters.query.name
        return UserResponseSpec(id=1, name=user_name)

    @api.body(UserCreateSpec)
    @api.response(UserResponseSpec)
    def post(self, parameters: RequestParametersType):
        user_name = parameters.body.name
        user_password = parameters.body.password
        return UserResponseSpec(id=1, name=user_name)


app.add_url_rule("/user", view_func=User.as_view("user"))
```

## Use decorators
You can use decorators to make spec document and validate request parameters. When using decorators, you don’t need to care about the order.
 
| Decorator                             | Description                               |
| -----------                           | ------------------------------------      |
| [`Path`](/decorators/path/)           | Receive request url path                  |
| [`Query`](/decorators/query/)         | Receive request query string              |
| [`Header`](/decorators/header/)       | Receive request header                    |
| [`Body`](/decorators/body/)           | Receive request body                      |
| [`Form`](/decorators/form/)           | Receive request form data                 |
| [`Auth`](/decorators/auth/)           | Receive authorization token by headers    |
| [`Response`](/decorators/response/)   | Make response schema to spec document     |


```python hl_lines="26 27 33 34"
from flask import Flask
from flask.views import MethodView
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


class User(MethodView):
    @api.query(UserGetSpec)
    @api.response(UserResponseSpec)
    def get(self, parameters: RequestParametersType):
        """Get a user name and id"""
        user_name = parameters.query.name
        return UserResponseSpec(id=1, name=user_name)

    @api.body(UserCreateSpec)
    @api.response(UserResponseSpec)
    def post(self, parameters: RequestParametersType):
        user_name = parameters.body.name
        user_password = parameters.body.password
        return UserResponseSpec(id=1, name=user_name)


app.add_url_rule("/user", view_func=User.as_view("user"))
```

## Get parameters
You can get request args from "parameters". except for response, all decorators will store the initialized objects on request.parameters.`<Decorator name>`.
!!! Note
    Decorator will pass request.parameters to the function.

```python hl_lines="30 36 37"
from flask import Flask
from flask.views import MethodView
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


class User(MethodView):
    @api.query(UserGetSpec)
    @api.response(UserResponseSpec)
    def get(self, parameters: RequestParametersType):
        """Get a user name and id"""
        user_name = parameters.query.name
        return UserResponseSpec(id=1, name=user_name)

    @api.body(UserCreateSpec)
    @api.response(UserResponseSpec)
    def post(self, parameters: RequestParametersType):
        user_name = parameters.body.name
        user_password = parameters.body.password
        return UserResponseSpec(id=1, name=user_name)


app.add_url_rule("/user", view_func=User.as_view("user"))
```

## Return response
If you return an object of BaseModel type, the response decorator will automatically convert it into a dictionary. When flask captures a dictionary, it will be processed by jsonify and output.

```python hl_lines="31 38"
from flask import Flask
from flask.views import MethodView
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


class User(MethodView):
    @api.query(UserGetSpec)
    @api.response(UserResponseSpec)
    def get(self, parameters: RequestParametersType):
        """Get a user name and id"""
        user_name = parameters.query.name
        return UserResponseSpec(id=1, name=user_name)

    @api.body(UserCreateSpec)
    @api.response(UserResponseSpec)
    def post(self, parameters: RequestParametersType):
        user_name = parameters.body.name
        user_password = parameters.body.password
        return UserResponseSpec(id=1, name=user_name)


app.add_url_rule("/user", view_func=User.as_view("user"))
```

## Interactive API docs 
Swagger ui docs => [http://localhost:5000/docs](http://localhost:5000/docs).  
If you want to access spec.json, you can go to [http://localhost/api/sepc.json](http://localhost/api/sepc.json)

![](images/quickstart.png)