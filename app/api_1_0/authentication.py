from flask import g, jsonify
from flask_jwt import JWT

from ..models import User
from .errors import bad_request, unauthorized, forbidden


# create an instance of flask-jwt:
jwt = JWT()

# define it's flask-jwtjwt callbacks:

@jwt.authentication_handler
def authenticate(email, password):
    """ Handles the authentication of users when requests 
        is made to the jwt authentication endpoint i.e '\login'.
        Returns the authenticated user or the default None.
    """
    if email and password:
        user = User.query.filter_by(email=email).first()
        if user and user.verify_password(password):
            g.current_user = user
            return user


@jwt.identity_handler
def identity(payload):
    """ Resolves and returns the autenticated user from the jwt payload.
        This is used to set the jwt current_identity object 
        in the context of protected endpoints. 
    """
    return User.query.filter(User.id == payload['identity']).first()


@jwt.auth_response_handler
def auth_response(access_token, identity):
    """ Defines the response to an authenticated user
    """
    return jsonify({
        'access_token': access_token.decode('utf-8'),
        'profile': identity.to_json()
    })
    return unauthorized(error.error)