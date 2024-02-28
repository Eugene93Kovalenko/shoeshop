import logging

from django.contrib.postgres.search import SearchVector, SearchQuery
from django.utils import timezone

from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from .forms import ContactForm, ReviewForm
from .models import *
from . import tasks
from .queries import get_filtered_products, get_all_categories, get_all_sizes, get_all_brands, \
    get_all_colors, get_ordering_option, get_product_from_slug, get_single_product_images, \
    get_single_product_variations, get_single_product_reviews, get_single_product_reviews_quantity, \
    create_product_review, get_ratings_count, get_queryset_after_search, get_all_images
from .services import get_average_rating, update_recently_viewed_session, get_ordering_from_request, \
    get_brands_list_from_request, get_sizes_list_from_request, get_categories_list_from_request, \
    get_colors_list_from_request

logger = logging.getLogger(__name__)


class HomeView(generic.ListView):
    model = Product
    template_name = "products/index.html"
    context_object_name = "images"

    def get_queryset(self):
        return get_all_images()


class ShopView(generic.ListView):
    model = Product
    template_name = "products/shop.html"
    # context_object_name = "products"
    context_object_name = "images"
    paginate_by = 4

    # def get_filters(self):
    #     brand_q, size_q, category_q, color_q = Q(), Q(), Q(), Q()
    #
    #     brands = get_brands_list_from_request(self.request)
    #     if brands:
    #         for brand in brands:
    #             brand_q |= Q(brand__name=brand)
    #     sizes = get_sizes_list_from_request(self.request)
    #     if sizes:
    #         for size in sizes:
    #             size_q |= Q(product_variation__size__name=size)
    #     categories = get_categories_list_from_request(self.request)
    #     if categories:
    #         for category in categories:
    #             category_q |= Q(category__name=category)
    #     colors = get_colors_list_from_request(self.request)
    #     if colors:
    #         for color in colors:
    #             color_q |= Q(color__name=color)
    #     return brand_q & size_q & category_q & color_q

    def get_filters(self):
        brand_q, size_q, category_q, color_q = Q(), Q(), Q(), Q()

        brands = get_brands_list_from_request(self.request)
        if brands:
            for brand in brands:
                brand_q |= Q(product__brand__name=brand)
        sizes = get_sizes_list_from_request(self.request)
        if sizes:
            for size in sizes:
                size_q |= Q(product__product_variation__size__name=size)
        categories = get_categories_list_from_request(self.request)
        if categories:
            for category in categories:
                category_q |= Q(product__category__name=category)
        colors = get_colors_list_from_request(self.request)
        if colors:
            for color in colors:
                color_q |= Q(product__color__name=color)
        return brand_q & size_q & category_q & color_q

    def get_ordering(self):
        return get_ordering_from_request(self.request)

    def get_gender_filter(self):
        gender_variations = {
            '/shop/women/': {'gender__name': 'Women'},
            '/shop/men/': {'gender__name': 'Men'},
        }
        gender_filter = gender_variations.get(self.request.path, {})
        return gender_filter

    def get_queryset(self):
        return get_filtered_products(self.get_filters(), self.get_ordering(), self.get_gender_filter())

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ordering_options'] = get_ordering_option()
        context['brands_list'] = get_all_brands()
        context['sizes_list'] = get_all_sizes()
        context['categories_list'] = get_all_categories()
        context['colors_list'] = get_all_colors()
        context['selected_ordering'] = self.request.GET.get('ordering', '')
        context['selected_brand'] = get_brands_list_from_request(self.request)
        context['selected_size'] = [int(size) for size in get_sizes_list_from_request(self.request)]
        context['selected_category'] = get_categories_list_from_request(self.request)
        context['selected_color'] = get_colors_list_from_request(self.request)
        return context


class SearchView(ShopView):
    def get_queryset(self):
        query = self.request.GET.get("q")
        search_vector = SearchVector("name", "description")
        search_query = SearchQuery(query)
        searched_queryset = get_queryset_after_search(super().get_queryset(), search_vector, search_query)
        return searched_queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q')
        return context


class ProductView(generic.View):
    def get(self, request, *args, **kwargs):
        view = ProductDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ProductFormView.as_view()
        return view(request, *args, **kwargs)


class ProductDetailView(generic.DetailView):
    model = Product
    template_name = "products/product-detail.html"
    context_object_name = "product"
    slug_url_kwarg = "product_slug"

    def get(self, request, *args, **kwargs):
        update_recently_viewed_session(self.request.session, self.kwargs['product_slug'])
        current_product = get_product_from_slug(self.kwargs["product_slug"])
        current_product.last_visit = timezone.now()
        current_product.save()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs["product_slug"]
        context["form"] = ReviewForm()
        context["product_images"] = get_single_product_images(slug)
        context['list_of_product_sizes'] = [product.size for product in get_single_product_variations(slug)]
        context['product_reviews'] = get_single_product_reviews(slug)
        logger.debug(context['product_reviews'])
        context['reviews_quantity'] = get_single_product_reviews_quantity(slug)
        context['average_rating'] = get_average_rating(slug)
        ratings_count = get_ratings_count(slug)
        for rating_count in ratings_count:
            context[f'count_of_{rating_count["rate"]}_star_reviews'] = rating_count['count']
            context[f'percentage_of_{rating_count["rate"]}_star_reviews'] = rating_count['percent']
        return context


class ProductFormView(generic.FormView):
    model = Product
    template_name = "products/product-detail.html"
    form_class = ReviewForm

    def post(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            return redirect('accounts:login')
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        product = get_product_from_slug(self.kwargs["product_slug"])
        form_data = form.cleaned_data
        create_product_review(
            product,
            form_data['rate'],
            form_data['text'],
            self.request.user,
            form_data['first_name'],
            form_data['last_name']
        )
        return super(ProductFormView, self).form_valid(form)

    def get_success_url(self):
        return reverse('products:home')


class ContactView(generic.FormView):
    template_name = "products/contact.html"
    form_class = ContactForm

    def form_valid(self, form):
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        sender = form.cleaned_data['email']
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']

        tasks.send_email_from_contact_form.delay(first_name, last_name, sender, subject, message)
        return super(ContactView, self).form_valid(form)

    def get_success_url(self):
        return reverse('products:home')


class AboutView(generic.TemplateView):
    template_name = "products/about.html"
