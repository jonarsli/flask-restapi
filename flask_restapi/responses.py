from flask import Response, jsonify


class JSONResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, dict):
            response = jsonify(response)
        return super(JSONResponse, cls).force_type(response, environ)


class ErrorResponse(Response):
    default_mimetype = "application/json"
