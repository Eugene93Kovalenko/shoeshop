from django.db.models import Avg, Count, ExpressionWrapper, F, DecimalField
from django.shortcuts import get_object_or_404

from products.models import Product, Brand, Size, Category, Color, ProductImage, ProductVariation, Review


def get_all_products():
    return Product.objects.all()


def get_filtered_products(filters, ordering, gender_filter):
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





def get_product_from_slug(slug):
    return Product.objects.get(slug=slug)


def get_single_product_images(slug):
    return ProductImage.objects.filter(product__slug=slug)


def get_single_product_variations(slug):
    return ProductVariation.objects.filter(product__slug=slug)


def get_single_product_reviews(slug):
    return Review.objects.filter(product__slug=slug)


def get_single_product_reviews_quantity(slug):
    return Review.objects.filter(product__slug=slug).count()


def get_single_product_rating(slug):
    return Review.objects.filter(product__slug=slug).aggregate(average=Avg('rate', default=0))


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


def get_ratings_count(slug):
    ratings_count = get_single_product_reviews(slug) \
        .values('rate') \
        .annotate(count=Count('rate')) \
        .annotate(percent=ExpressionWrapper((F('count') * 100) / get_single_product_reviews_quantity(slug),
                                            output_field=DecimalField()))
    return ratings_count
