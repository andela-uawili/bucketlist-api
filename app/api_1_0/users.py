from flask import jsonify, request, current_app, url_for, g, abort
from . import api
from .. import db
from ..models import User, Bucketlist, BucketlistItem
from .errors import bad_request, unauthorized, forbidden


@api.route('/auth/register', methods = ['POST'])
def register_user():
    """ Registers a new user. 
    """
    # get the json data:
    email = request.json.get('email')
    password = request.json.get('password')
    username = request.json.get('username')
    
    # valideate the registration credentials:
    if email is None or password is None:
        return bad_request("missing email or password")
    if User.query.filter_by(email=email).first() is not None:
         abort(400) # existing user
    
    # create the user and save to the db:
    user = User(email=email, password=password, username=username)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_json()), 201


@api.route('/auth/login', methods = ['POST'])
def login_user():
    """ login an existing user. 
    """