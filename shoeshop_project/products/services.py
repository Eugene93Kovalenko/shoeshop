from products.queries import get_single_product_rating


def round_int_custom(num, step):
    return round(num / step) * step


def get_average_rating(slug):
    average_product_rating = get_single_product_rating(slug)
    if not average_product_rating:
        return None
    return round_int_custom(float(average_product_rating['average']), 0.5)


def update_recently_viewed_session(session, slug):
    if 'recently_viewed' not in session:
        session['recently_viewed'] = slug
    else:
        if slug in session['recently_viewed']:
            session['recently_viewed'].remove(slug)
        session['recently_viewed'].insert(0, slug)
        if len(session['recently_viewed']) > 4:
            session['recently_viewed'].pop()
    session.modified = True


def get_ordering_from_request(request):
    return request.GET.get('ordering', '')


def get_brands_list_from_request(request):
    return request.GET.getlist('brands')


def get_sizes_list_from_request(request):
    return request.GET.getlist('sizes')


def get_categories_list_from_request(request):
    return request.GET.getlist('categories')


def get_colors_list_from_request(request):
    return request.GET.getlist('colors')

