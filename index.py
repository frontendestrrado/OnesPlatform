from flask import Blueprint, redirect


index_blueprint = Blueprint('index_blueprint', __name__)


@index_blueprint.route('/')
def index():
    return redirect('ads/upload')

