from flask import jsonify, request, current_app, url_for, g, abort
from flask_jwt import jwt_required, current_identity

from ..models import User, Bucketlist, BucketlistItem
from .. import db
from . import api
from .errors import bad_request, unauthorized, forbidden


@api.route('/auth/register', methods = ['POST'])
def register_user():
    """ Registers a new user. 
    """
    # get the json data:
    email = request.json.get('email')
    password = request.json.get('password')
    username = request.json.get('username')
    
    # validate the registration credentials:
    if email is None or password is None:
        return bad_request("missing email or password")
    if User.query.filter_by(email=email).first() is not None:
         abort(400) # existing user
    
    # create the user and save to the db:
    user = User(email=email, password=password, username=username)
    db.session.add(user)
    db.session.commit()
    return jsonify({
        "username": str(user),
        "login_url": url_for('login', _external=True)
    }), 201


@api.route('/users/<int:id>', methods = ['GET'])
@jwt_required()
def get_user(id):
    """ Returns profile of user specifed by id. 
    """
    user = User.query.filter_by(id=id).first()
    if user:
        return jsonify(user.to_json()), 200
    else:
        return bad_request("User does not exist")
    