from flask import Blueprint, render_template

from .spec import spec

restapi_bp = Blueprint("restapi", __name__, template_folder="templates")


def get_spec():
    return spec.spec_model.dict(exclude_none=True)


def get_swagger_docs():
    return render_template("swagger_ui.html")
