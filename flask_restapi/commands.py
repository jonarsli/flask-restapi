import click
from flask.cli import AppGroup

from .tool import core, template

api_cli = AppGroup("api")


@api_cli.command("create")
@click.argument("name", required=True, type=str)
def create(name: str):
    # Create app
    core.create_directory(name)
    core.create_file(f"{name}/__init__.py", template.get_init_template(name))
    # Create routes
    core.create_file(f"{name}/routes.py", template.get_routes_template())
    # Create errors
    core.create_file(f"{name}/errors.py", template.get_errors_template())
    # Create views
    core.create_directory(f"{name}/views")
    core.create_file(f"{name}/views/__init__.py")
    # Create specs
    core.create_directory(f"{name}/specs")
    core.create_file(f"{name}/specs/__init__.py")
    # Create services
    core.create_directory(f"{name}/services")
    core.create_file(f"{name}/services/__init__.py")
