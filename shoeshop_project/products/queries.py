from django.contrib.postgres.search import SearchRank
from django.db.models import Avg, Count, ExpressionWrapper, F, DecimalField
from django.shortcuts import get_object_or_404

from products.models import Product, Brand, Size, Category, Color, ProductImage, ProductVariation, Review


def get_all_images():
    return ProductImage.objects.select_related('product').filter(is_main=True).order_by('product__purchases_count')[:8]


def get_filtered_products(filters, ordering, gender_filter):
    product_images = ProductImage.objects.select_related('product').filter(filters, **gender_filter,
                                                                           is_main=True).distinct()
    if ordering:
        return product_images.order_by(ordering)
    return product_images


def get_all_brands():
    return Brand.objects.values('name')


def get_all_sizes():
    return Size.objects.values('name')


def get_all_categories():
    return Category.objects.values('name')


def get_all_colors():
    return Color.objects.values('name')


def get_ordering_option():
    return Product.ORDERING_OPTIONS


def get_single_product(product_id):
    return get_object_or_404(Product, id=product_id)


def get_single_product_images(product_id):
    return ProductImage.objects.filter(product__id=product_id)


def get_single_product_sizes(product_id):
    return ProductVariation.objects.filter(product__id=product_id). \
        values_list('size__name', flat=True). \
        distinct()


def get_single_product_rating(product_id):
    return Review.objects.filter(product__id=product_id).aggregate(average=Avg('rate', default=0))


def create_product_review(product, rate, text, user, first_name, last_name):
    review = Review.objects.create(
        product=product,
        rate=rate,
        text=text,
        user=user,
        first_name=first_name,
        last_name=last_name
    )
    review.save()


def get_single_product_reviews(product_id):
    return Review.objects.filter(product__id=product_id)


def get_single_product_reviews_quantity(product_id):
    return Review.objects.filter(product__id=product_id).count()


def get_ratings_count(product_id, reviews_quantity):
    ratings_count = get_single_product_reviews(product_id) \
        .values('rate') \
        .annotate(count=Count('rate')) \
        .annotate(percent=ExpressionWrapper((F('count') * 100) / reviews_quantity, output_field=DecimalField()))
    return ratings_count


def get_queryset_after_search(queryset, search_vector, search_query):
    queryset = queryset.annotate(
        search=search_vector,
        rank=SearchRank(search_vector, search_query)) \
        .filter(rank__gte=0.1).order_by('-rank')
    return queryset
