from flask import jsonify, request, current_app, url_for, g
from flask_jwt import jwt_required, current_identity

from ..models import Bucketlist
from .. import db
from . import api
from .errors import bad_request, unauthorized, forbidden, not_found


@api.route('/bucketlists/', methods = ['GET'])
@jwt_required()
def get_bucketlists():
    """ gets all [or searches] the bucketlists created by the current user. 
    """
    # fetch the pagination options:
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', current_app.config['DEFAULT_PER_PAGE'], type=int)
    
    # ensure that items per page does not pass the maximum:
    max_per_page = current_app.config['MAX_PER_PAGE']
    if per_page > max_per_page:
        per_page = max_per_page

    # fetch any search key specified:
    q = request.args.get('q', "", type=str)

    # paginate user's [searched] bucketlists:
    pagination = Bucketlist.query.\
                 filter_by(created_by=current_identity).\
                 filter(Bucketlist.name.like("%{}%".format(q))).\
                 paginate( page,
                           per_page=per_page,
                           error_out=False)
    
    # get current page of user's bucketlists:
    bucketlists = pagination.items
    
    # get url to the previous page:
    prev_url = url_for('api.get_bucketlists', page=page-1, _external=True)\
               if pagination.has_prev else None
    
    # get url for the next page:
    next_url = url_for('api.get_bucketlists', page=page+1, _external=True)\
               if pagination.has_next else None
    
    # return the json response:
    return jsonify({
        "bucketlists": [bucketlist.to_json() for bucketlist in bucketlists],
        "current_page": page,
        "total": pagination.total,
        "next_url": next_url,
        "prev_url": prev_url,
    }), 200



@api.route('/bucketlists/<int:id>', methods = ['GET'])
@jwt_required()
def get_bucketlist(id):
    """ get an existing bucketlist. 
    """

    # get the bucketlist:
    bucketlist = Bucketlist.query.\
                 filter_by(created_by=current_identity).\
                 filter_by(id=id).\
                 first()
    if not bucketlist:
        return not_found('Item does not exist')

    # get its items as a queryset (because lazy='dynamic'):
    bucketlist_items_query = bucketlist.items

    # fetch the pagination options:
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', current_app.config['DEFAULT_PER_PAGE'], type=int)
    
    # ensure that items per page does not pass the maximum:
    max_per_page = current_app.config['MAX_PER_PAGE']
    if per_page > max_per_page:
        per_page = max_per_page

    # paginate user's [searched] bucketlists:
    pagination = bucketlist_items_query.paginate( page, per_page=per_page, error_out=False)
    
    # get current page of user's bucketlists:
    bucketlist_items = pagination.items
    
    # get url to the previous page:
    prev_url = None
    if pagination.has_prev:
        prev_url = url_for('api.get_bucketlist', 
                            id=bucketlist.id,  
                            page=page-1, 
                            limit=per_page, 
                            _external=True)
    
    # get url for the next page:
    next_url = None
    if pagination.has_next:
        next_url = url_for('api.get_bucketlist', 
                            id=bucketlist.id, 
                            page=page+1, 
                            limit=per_page, 
                            _external=True)
    
    # get 
    bucketlist_json = bucketlist.to_json()
    bucketlist_json['items'] = [bucketlist_item.to_json() for bucketlist_item in bucketlist_items]


    # return the json response:
    return jsonify({
        "bucketlist": bucketlist_json,
        "current_page": page,
        "total": pagination.total,
        "next_url": next_url,
        "prev_url": prev_url,
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
    bucketlist = Bucketlist.query.\
                 filter_by(created_by=current_identity).\
                 filter_by(id=id).\
                 first()
    if not bucketlist:
        return not_found('Item does not exist')

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
    bucketlist = Bucketlist.query.\
                 filter_by(created_by=current_identity).\
                 filter_by(id=id).\
                 first()
    if not bucketlist:
        return not_found('Item does not exist')

    # delete the bucketlist from the db:
    db.session.delete(bucketlist)
    db.session.commit()

    # return the json response:
    return jsonify({
        "status": "deleted",
        "bucketlists_url": url_for('api.get_bucketlists', _external=True)
    }), 200