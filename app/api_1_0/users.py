from flask import jsonify, request, current_app, url_for
from . import api
# from ..models import User, Post

@api.route('/users/<int:id>/')
def get_users(id):
    return "Hello! {}".format(id)