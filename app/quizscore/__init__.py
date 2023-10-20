from flask import Blueprint

quizscore_blueprint = Blueprint("quizscore", __name__, url_prefix="/quizscore")

from . import routes