from flask import Blueprint

workflow = Blueprint('workflow', __name__)

from . import views