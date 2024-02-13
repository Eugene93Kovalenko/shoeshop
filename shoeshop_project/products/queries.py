from products.models import Product, Brand, Size, Category, Color


def get_all_products():
    return Product.objects.all()


def get_filtered_products_for_shop_view(filters, ordering, gender_filter):
    if ordering:
        return Product.objects.filter(filters, **gender_filter).order_by(ordering).distinct()
    return Product.objects.filter(filters, **gender_filter).distinct()


def get_all_brands():
    return Brand.objects.all()


def get_all_sizes():
    return Size.objects.all()


def get_all_categories():
    return Category.objects.all()


def get_all_colors():
    return Color.objects.all()


def get_ordering_option():
    return Product.ORDERING_OPTIONS
