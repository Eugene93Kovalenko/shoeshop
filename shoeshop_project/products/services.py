from django.core.handlers.wsgi import WSGIRequest

from products.queries import get_single_product_rating


def round_int_custom(num: float, step: float) -> float:
    return round(num / step) * step


def get_average_rating(product_id: str) -> float | None:
    average_product_rating = get_single_product_rating(product_id)
    if not average_product_rating:
        return None
    return round_int_custom(float(average_product_rating['average']), 0.5)


def get_ordering_from_request(request: WSGIRequest) -> str | None:
    ordering = request.GET.get('ordering', '')
    if ordering == '-purchases_count':
        return '-product__popularity'
    elif ordering == '-last':
        return '-product__created_at'
    elif ordering == '-price':
        return '-product__actual_price'
    elif ordering == 'price':
        return 'product__actual_price'
