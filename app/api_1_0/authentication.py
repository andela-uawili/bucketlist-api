from collections import OrderedDict

from flask import jsonify, url_for, g
from flask_jwt import JWT

from .. import db
from ..models import User
from .errors import bad_request, unauthorized, forbidden


# create an instance of flask-jwt:
jwt = JWT()


# define the flask-jwt callbacks:

@jwt.authentication_handler
def authenticate(email, password):
    """ Handles the authentication of users when requests 
        is made to the jwt authentication endpoint i.e '\login'.
        Returns the authenticated user or the default None.
    """
    if email and password:
        user = User.query.filter_by(email=email).first()
        if user and user.verify_password(password):

            # set the logged-in status flag for the authenticated user:
            user.logged_in = True
            db.session.add(user)
            db.session.commit()

            return user


@jwt.identity_handler
def identity(payload):
    """ Resolves and returns the autenticated user from the jwt payload.
        This is used to set the jwt current_identity object 
        in the context of protected endpoints. 
        Also verifies that a user is logged in before proceeding with request.
    """
    user = User.query.filter(User.id == payload['identity']).first()
    if user and user.logged_in:
        return user


@jwt.auth_response_handler
def auth_response(access_token, identity):
    """ Defines the response to an authenticated user
    """
    # return the json resons with token:
    return jsonify({
        'access_token': access_token.decode('utf-8'),
        'profile': identity.to_json(),
        'bucketlists_url': url_for('api.get_bucketlists', _external=True),
    })


@jwt.jwt_error_handler
def jwt_error_handler(error):
    """ overrides the built-in flask-jwt error FILE_UPLOAD_HANDLERS
        to add support for logged-in status reporting.
    """
    if error.error == 'Invalid JWT':
        error.description = 'User not logged in or does not exist'

    return jsonify({
        'status_code': error.status_code,
        'error': error.error,
        'description': error.description,
    }), error.status_code, error.headers