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
    bucketlist = Bucketlist.query.\
                 filter_by(created_by=current_identity).\
                 filter_by(id=id).\
                 first()
    if not bucketlist:
        return not_found('Item does not exist')

    # get new bucketlist-item:
    bucketlist_item = BucketlistItem.from_json(request.json)

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



@api.route('/bucketlists/<int:id>/items/<int:item_id>', methods = ['PUT'])
@jwt_required()
def update_bucketlist_item(id, item_id):
    """ updates an existing bucketlist item. 
    """
    # get the bucketlist:
    bucketlist = Bucketlist.query.\
                 filter_by(created_by=current_identity).\
                 filter_by(id=id).\
                 first()
    if not bucketlist:
        return not_found('Item does not exist')

    # get bucketlist-item:
    bucketlist_item = BucketlistItem.query.\
                      filter_by(bucketlist=bucketlist).\
                      filter_by(id=item_id).\
                      first()
    if not bucketlist_item:
        return not_found('Item does not exist')

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



@api.route('/bucketlists/<int:id>/items/<int:item_id>', methods = ['DELETE'])
@jwt_required()
def delete_bucketlist_item(id, item_id):
    """ deletes an existing bucketlist-item. 
    """
    # get the bucketlist:
    bucketlist = Bucketlist.query.\
                 filter_by(created_by=current_identity).\
                 filter_by(id=id).\
                 first()
    if not bucketlist:
        return not_found('Item does not exist')

    # get bucketlist-item:
    bucketlist_item = BucketlistItem.query.\
                      filter_by(bucketlist=bucketlist).\
                      filter_by(id=item_id).\
                      first()
    if not bucketlist_item:
        return not_found('Item does not exist')

    # delete the bucketlist from the db:
    db.session.delete(bucketlist_item)
    db.session.commit()

    # return the json response:
    return jsonify({
        "status": "deleted",
        "bucketlist_url": url_for('api.get_bucketlist', id=bucketlist.id, _external=True)
    }), 200 