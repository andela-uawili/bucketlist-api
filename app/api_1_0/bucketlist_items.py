from flask import jsonify, request, current_app, url_for, g
from flask_jwt import jwt_required, current_identity

from ..models import User, Bucketlist, BucketlistItem
from .. import db
from . import api
from .errors import bad_request, unauthorized, forbidden, not_found


@api.route('/bucketlists/<int:id>/items/', methods = ['POST'])
@jwt_required()
def create_bucketlist_item(id):
    """ creates a new bucketlist-item in the specified bucketlist. 
    """
    # get the bucketlist:
    try:
        bucketlist = Bucketlist.get_user_bucketlist(current_identity, id)
    except Exception, e:
        return not_found(e.message)

    # get new bucketlist-item:
    bucketlist_item = BucketlistItem.from_json(request.json)

    # ensure a bucketlist-item has a name:
    if not bucketlist_item.name:
        return bad_request('A bucketlist-item must have a name')

    # associate the bucketlist_item with the bucketlist:
    bucketlist_item.bucketlist = bucketlist

    # save the bucketlist to the db:
    db.session.add(bucketlist_item)
    db.session.commit()

    # return the json response:
    return jsonify({
        "bucketlist_item": bucketlist_item.to_json(),
        "bucketlist_url": url_for('api.get_bucketlist', id=bucketlist.id, _external=True)
    }), 201


@api.route('/bucketlists/<int:id>/items/<int:item_id>', methods = ['PUT', 'DELETE'])
@jwt_required()
def manage_bucketlist_item(id, item_id):
    """ updates or deletes an existing bucketlist item. 
    """
    # get the bucketlist:
    try:
        bucketlist = Bucketlist.get_user_bucketlist(current_identity, id)
    except Exception, e:
        return not_found(e.message)

    # get bucketlist-item:
    try:
        bucketlist_item = BucketlistItem.get_bucketlist_item(bucketlist, item_id)
    except Exception, e:
        return not_found(e.message)
    
    if request.method == 'PUT':
        # update it with the json values:
        json_bucketlist_item = request.json
        name = json_bucketlist_item.get('name')
        done = json_bucketlist_item.get('done')
        
        if name:
            bucketlist_item.name = name
        if isinstance(done, bool):
            bucketlist_item.done = done

        # save the bucketlist_item to the db:
        db.session.add(bucketlist_item)
        db.session.commit()

        # return the json response:
        return jsonify({
            "bucketlist_item": bucketlist_item.to_json(),
            "bucketlist_url": url_for('api.get_bucketlist', id=bucketlist.id, _external=True)
        }), 200

    elif request.method == 'DELETE':
         # delete the bucketlist from the db:
        db.session.delete(bucketlist_item)
        db.session.commit()

        # return the json response:
        return jsonify({
            "status": "deleted",
            "bucketlist_url": url_for('api.get_bucketlist', id=bucketlist.id, _external=True)
        }), 200

     