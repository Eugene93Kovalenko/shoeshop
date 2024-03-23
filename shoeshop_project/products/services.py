from products.queries import get_single_product_rating


def round_int_custom(num, step):
    return round(num / step) * step


def get_average_rating(product_uuid):
    average_product_rating = get_single_product_rating(product_uuid)
    if not average_product_rating:
        return None
    return round_int_custom(float(average_product_rating['average']), 0.5)


def update_recently_viewed_session(session, product_id):
    product_id = str(product_id)
    recently_viewed = session.setdefault('recently_viewed', [])

    if product_id in recently_viewed:
        recently_viewed.remove(product_id)

    recently_viewed.insert(0, product_id)
    session['recently_viewed'] = recently_viewed[:4]
    session.modified = True


def get_ordering_from_request(request):
    ordering = request.GET.get('ordering', '')
    if ordering == '-purchases_count':
        return '-product__popularity'
    elif ordering == '-last':
        return '-product__created_at'
    elif ordering == '-price':
        return '-product__actual_price'
    elif ordering == 'price':
        return 'product__actual_price'
