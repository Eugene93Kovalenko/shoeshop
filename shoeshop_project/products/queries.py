from django.contrib.postgres.search import SearchRank, SearchVector, CombinedSearchVector, SearchQuery
from django.db.models import Avg, Count, ExpressionWrapper, F, DecimalField, Q, QuerySet
from django.shortcuts import get_object_or_404

from accounts.models import CustomUser
from products.models import Product, Brand, Size, Category, Color, ProductImage, ProductVariation, Review


def get_all_images() -> QuerySet[ProductImage]:
    return ProductImage.objects.select_related('product').filter(is_main=True).order_by('product__purchases_count')[:8]


def get_filtered_products(filters: Q, ordering: str | None, gender_filter: dict[str: str]) -> QuerySet[ProductImage]:
    product_images = ProductImage.objects.select_related('product'). \
        filter(filters, **gender_filter, is_main=True).distinct()
    if ordering:
        return product_images.order_by(ordering)
    return product_images


def get_all_brands() -> QuerySet[dict[str, str]]:
    return Brand.objects.values('name')


def get_all_sizes() -> QuerySet[dict[str, int]]:
    return Size.objects.values('name')


def get_all_categories() -> QuerySet[dict[str, str]]:
    return Category.objects.values('name')


def get_all_colors() -> QuerySet[dict[str, str]]:
    return Color.objects.values('name')


def get_ordering_option() -> list[tuple[str, str]]:
    return Product.ORDERING_OPTIONS


def get_single_product(product_id: str) -> Product | None:
    return get_object_or_404(Product, id=product_id)


def get_single_product_images(product_id: str) -> QuerySet[ProductImage]:
    return ProductImage.objects.filter(product__id=product_id)


def get_single_product_sizes(product_id: str) -> QuerySet[ProductVariation]:
    return ProductVariation.objects.filter(product__id=product_id). \
        values_list('size__name', flat=True). \
        distinct()


def get_single_product_rating(product_id: str) -> QuerySet[Review]:
    return Review.objects.filter(product__id=product_id).aggregate(average=Avg('rate', default=0))


def create_product_review(
        product: Product,
        rate: int,
        text: str,
        user: CustomUser,
        first_name: str,
        last_name: str) -> None:

    review = Review.objects.create(
        product=product,
        rate=rate,
        text=text,
        user=user,
        first_name=first_name,
        last_name=last_name
    )
    review.save()


def get_single_product_reviews(product_id: str) -> QuerySet[Review]:
    return Review.objects.filter(product__id=product_id)


def get_single_product_reviews_quantity(product_id: str) -> int:
    return Review.objects.filter(product__id=product_id).count()


def get_ratings_count(product_id: str, reviews_quantity: int) -> QuerySet[Review]:
    ratings_count = get_single_product_reviews(product_id) \
        .values('rate') \
        .annotate(count=Count('rate')) \
        .annotate(percent=ExpressionWrapper((F('count') * 100) / reviews_quantity, output_field=DecimalField()))
    return ratings_count


def get_queryset_after_search(
        queryset: QuerySet[ProductImage],
        search_vector: CombinedSearchVector,
        search_query: SearchQuery) -> QuerySet[ProductImage]:

    queryset = queryset.annotate(
        search=search_vector,
        rank=SearchRank(search_vector, search_query)) \
        .filter(rank__gte=0.1).order_by('-rank')
    return queryset
