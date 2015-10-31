from flask import jsonify, request, current_app, url_for, g
from flask_jwt import jwt_required, current_identity

from ..models import Bucketlist
from .. import db
from . import api
from .utils import paginate
from .errors import bad_request, unauthorized, forbidden, not_found


@api.route('/bucketlists/', methods = ['GET'])
@jwt_required()
def get_bucketlists():
    """ gets all [or searches] the bucketlists created by the current user. 
    """
    # fetch the pagination and search options from the request:
    options = request.args.copy()

    # get/search user's bucketlists:
    results = Bucketlist.query.filter_by(created_by=current_identity)

    # search if key isspecified:
    q = options.get('q', type=str)
    if q:
        results = results.filter(Bucketlist.name.ilike("%{}%".format(q)))
    
    # paginate the results:
    paginated_results = paginate(results, 'api.get_bucketlists', options)
    
    # return the json response:
    return jsonify({
        "bucketlists": [bucketlist.to_json() for bucketlist in paginated_results.get('items')],
        "current_page": paginated_results.get('current_page'),
        "total": paginated_results.get('total'),
        "next_url": paginated_results.get('next_url'),
        "prev_url": paginated_results.get('prev_url'),
    }), 200


@api.route('/bucketlists/<int:id>', methods = ['GET'])
@jwt_required()
def get_bucketlist(id):
    """ get an existing bucketlist. 
    """
    # fetch the pagination and search options from the request:
    options = request.args.copy()

    # get the bucketlist:
    try:
        bucketlist = Bucketlist.get_user_bucketlist(current_identity, id)
    except Exception, e:
        return not_found(e.message)

    # get its items as a queryset (because lazy='dynamic'):
    bucketlist_items_query = bucketlist.items

    # paginate thebucketlist_items_query  results:
    options.update({'id': id})
    paginated_results = paginate(bucketlist_items_query, 'api.get_bucketlist', options)
    
    # prep the json repr:
    bucketlist_json = bucketlist.to_json()
    bucketlist_json['items'] = [bucketlist_item.to_json() for bucketlist_item in paginated_results.get('items')]

    # return the json response:
    return jsonify({
        "bucketlist": bucketlist_json,
        "current_page": paginated_results.get('current_page'),
        "total": paginated_results.get('total'),
        "next_url": paginated_results.get('next_url'),
        "prev_url": paginated_results.get('prev_url'),
        "bucketlists_url": url_for('api.get_bucketlists', _external=True)
    }), 200


@api.route('/bucketlists/', methods = ['POST'])
@jwt_required()
def create_bucketlist():
    """ creates a new bucketlist for the current user. 
    """
    # get new bucketlist:
    bucketlist = Bucketlist.from_json(request.json)

    # ensure a bucketlist has a name:
    if not bucketlist.name:
        return bad_request('A bucketlist must have a name')

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


@api.route('/bucketlists/<int:id>', methods = ['PUT', 'DELETE'])
@jwt_required()
def manage_bucketlist(id):
    """ updates or deletes an existing bucketlist. 
    """
    # get the bucketlist:
    try:
        bucketlist = Bucketlist.get_user_bucketlist(current_identity, id)
    except Exception, e:
        return not_found(e.message)

    if request.method == 'PUT':
        
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

    elif request.method == 'DELETE':

        # delete the bucketlist from the db:
        db.session.delete(bucketlist)
        db.session.commit()

        # return the json response:
        return jsonify({
            "status": "deleted",
            "bucketlists_url": url_for('api.get_bucketlists', _external=True)
        }), 200

    