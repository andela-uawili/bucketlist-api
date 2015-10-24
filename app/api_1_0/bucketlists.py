from flask import jsonify, request, current_app, url_for, g
from flask_jwt import jwt_required, current_identity

from ..models import User, Bucketlist, BucketlistItem
from .. import db
from . import api
from .errors import bad_request, unauthorized, forbidden, not_found


@api.route('/bucketlists/', methods = ['GET'])
@jwt_required()
def get_bucketlists():
    """ get all bucketlists for the current user. 
    """
    # get user's bucketlists:
    bucketlists = Bucketlist.query.filter_by(created_by=current_identity)
    
    # return the json response:
    return jsonify({
        "bucketlists": [bucketlist.to_json() for bucketlist in bucketlists],
        "bucketlists_url": url_for('api.get_bucketlists', _external=True)
    }), 200



@api.route('/bucketlists/<int:id>', methods = ['GET'])
@jwt_required()
def get_bucketlist(id):
    """ get an existing bucketlist. 
    """
    # get the bucketlist:
    bucketlist = Bucketlist.query.get(id)

    # ensure the bucketlist belongs to current user:
    if not bucketlist:
        return not_found('Item does not exist')
    if not bucketlist.created_by == current_identity:
        return forbidden('Invalid permissions')
    
    # return the json response:
    return jsonify({
        "bucketlist": bucketlist.to_json(),
        "bucketlists_url": url_for('api.get_bucketlists', _external=True)
    }), 200



@api.route('/bucketlists/', methods = ['POST'])
@jwt_required()
def create_bucketlist():
    """ creates a new bucketlist for the current user. 
    """
    # get new bucketlist:
    bucketlist = Bucketlist.from_json(request.json)

    # set the bucketlist creator to current user:
    bucketlist.created_by = current_identity

    # save the bucketlist to the db:
    db.session.add(bucketlist)
    db.session.commit()

    # return the json response:
    return jsonify({
        "bucketlist": bucketlist.to_json(),
        "bucketlists_url": url_for('api.get_bucketlists', _external=True)
    }), 201



@api.route('/bucketlists/<int:id>', methods = ['PUT'])
@jwt_required()
def update_bucketlist(id):
    """ updates an existing bucketlist. 
    """
    # get the bucketlist:
    bucketlist = Bucketlist.query.get(id)

    # ensure the bucketlist belongs to current user:
    if not bucketlist:
        return not_found('Item does not exist')
    if not bucketlist.created_by == current_identity:
        return forbidden('Invalid permissions')

    # update it with the json values:
    json_bucketlist = request.json
    name = json_bucketlist.get('name')
    if name:
        bucketlist.name = name

    # save the bucketlist to the db:
    db.session.add(bucketlist)
    db.session.commit()

    # return the json response:
    return jsonify({
        "bucketlist": bucketlist.to_json(),
        "bucketlists_url": url_for('api.get_bucketlists', _external=True)
    }), 200



@api.route('/bucketlists/<int:id>', methods = ['DELETE'])
@jwt_required()
def delete_bucketlist(id):
    """ deletes an existing bucketlist. 
    """
    # get the bucketlist:
    bucketlist = Bucketlist.query.get(id)
    # ensure the bucketlist belongs to current user:
    if not bucketlist:
        return not_found('Item does not exist')
    if not bucketlist.created_by == current_identity:
        return forbidden('Invalid permissions')

    # delete the bucketlist to the db:
    db.session.delete(bucketlist)
    db.session.commit()

    # return the json response:
    return jsonify({
        "status": "deleted",
        "bucketlists_url": url_for('api.get_bucketlists', _external=True)
    }), 200