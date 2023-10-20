from flask import Blueprint

choice_blueprint = Blueprint("choice", __name__, url_prefix="/choice")

from .import routes

