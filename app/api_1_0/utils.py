from flask import current_app, url_for


def paginate(queryset, endpoint, options):
    """ paginates a queryset 
    """
    # specify default page to show:
    page = options.get('page', 1, type=int)

    # specify default items per_page:
    limit = options.get('limit', current_app.config['DEFAULT_PER_PAGE'], type=int)

    # ensure that items per page does not pass the maximum
    max_per_page = current_app.config['MAX_PER_PAGE']
    if limit > max_per_page:
        limit = max_per_page

    # paginate queryset:
    pagination = queryset.paginate(page, per_page=limit, error_out=False)

    # update options to be used as url parameters:
    options = options.to_dict(); # converts from werkzeug multidict to dict
    options.update({'_external': True, 'limit': limit})
    
    # get url to the previous page:
    prev_url = None
    if pagination.has_prev:
        options['page'] = page-1
        prev_url = url_for(endpoint, **options)

    # get url for the next page:
    next_url = None
    if pagination.has_next:
        options['page'] = page+1
        next_url = url_for(endpoint, **options)

    # return the pagination results as a dict:
    return {
        "items": pagination.items,
        "current_page": page,
        "total": pagination.total,
        "next_url": next_url,
        "prev_url": prev_url,
    }