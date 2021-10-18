def get_init_template(app_name: str):
    return f"""from flask import Blueprint

bp = Blueprint('{app_name}', import_name=__name__)

def get_blueprint():
    from . import errors, routes

    return bp
"""


def get_routes_template():
    return """from . import bp
    """


def get_errors_template():
    return """from . import bp
    """
