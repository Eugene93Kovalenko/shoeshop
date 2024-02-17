from products.queries import get_single_product_rating


def round_int_custom(num, step):
    return round(num / step) * step


def get_average_rating(slug):
    average_product_rating = get_single_product_rating(slug)
    if not average_product_rating:
        return None
    return round_int_custom(float(average_product_rating['average']), 0.5)

