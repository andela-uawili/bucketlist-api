from flask import jsonify, request, current_app, url_for, g
from flask_jwt import jwt_required, current_identity

from ..models import User
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
        return forbidden("email not allowed to register")
    
    # create the user and save to the db:
    user = User(email=email, password=password, username=username)
    db.session.add(user)
    db.session.commit()

    # return json response:
    return jsonify({
        'username': str(user),
        'login_url': url_for('login', _external=True)
    }), 201


@api.route('/auth/logout', methods = ['GET'])
@jwt_required()
def logout():
    """ Logs the current user out. 
    """
    # set the logged-in status flag for the user:
    current_identity.logged_in = False
    db.session.add(current_identity)
    db.session.commit()

    # return json response:
    return jsonify({
        'status': 'logged out',
        'login_url': url_for('login', _external=True)
    }), 200


@api.route('/users/<int:id>', methods = ['GET'])
@jwt_required(id)
def get_user(id):
    """ Returns profile of user specifed by id. 
    """
    # get the user:
    user = User.query.get(id)
    if not user:
        return bad_request("User does not exist")

    # return json response:
    return jsonify({
        'profile': user.to_json(),
        'bucketlists_url': url_for('api.get_bucketlists', _external=True),
    }), 200


@api.route('/users/<int:id>', methods = ['PUT'])
@jwt_required()
def update_user(id):
    """ updates an existing user. 
    """
    # get the user:
    user = User.query.get(id)
    if not user:
        return bad_request("User does not exist")

    # update it with the json values:
    username = request.json.get('username')
    if username:
        user.username = username

    # save the user to the db:
    db.session.add(user)
    db.session.commit()

    # return the json response:
    return jsonify({
        "profile": user.to_json(),
        "bucketlists_url": url_for('api.get_bucketlists', _external=True)
    }), 200


@api.route('/users/<int:id>', methods = ['DELETE'])
@jwt_required()
def deregister_user(id):
    """ Removes an existing user account. 
    """
    # get the user:
    user = User.query.get(id)
    if not user:
        return bad_request("User does not exist")
    
    # remove the user from the db:
    db.session.delete(user)
    db.session.commit()
    
    # return json response:
    return jsonify({
        'status': 'deregistered',
        'registration_url': url_for('api.register_user', _external=True)
    }), 200