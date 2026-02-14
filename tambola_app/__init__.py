from flask import Blueprint

tambola_bp = Blueprint(
    "tambola",
    __name__,
    url_prefix="/tambola",
    template_folder="templates",
    static_folder="static"
)

from . import routes
