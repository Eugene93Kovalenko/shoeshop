import logging
from typing import Any

from django.contrib.postgres.search import SearchVector, SearchQuery

from django.db.models import Q, QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.views import generic

from .forms import ContactForm, ReviewForm
from .models import *
from . import tasks
from .queries import get_filtered_products, get_all_categories, get_all_sizes, get_all_brands, \
    get_all_colors, get_ordering_option, get_single_product, get_single_product_images, \
    get_single_product_reviews, get_single_product_reviews_quantity, \
    create_product_review, get_ratings_count, get_queryset_after_search, get_all_images, get_single_product_sizes
from .services import get_average_rating, get_ordering_from_request

logger = logging.getLogger(__name__)


class HomeView(generic.ListView):
    model = Product
    template_name = "products/index.html"
    context_object_name = "images"

    def get_queryset(self) -> QuerySet[ProductImage]:
        return get_all_images()


class ShopView(generic.ListView):
    model = Product
    template_name = "products/shop.html"
    context_object_name = "images"
    paginate_by = 9

    def get_filters(self) -> Q:
        brand_q, size_q, category_q, color_q = Q(), Q(), Q(), Q()

        brands = self.request.GET.getlist('brands')
        if brands:
            for brand in brands:
                brand_q |= Q(product__brand__name=brand)
        sizes = self.request.GET.getlist('sizes')
        if sizes:
            for size in sizes:
                size_q |= Q(product__product_variation__size__name=size)
        categories = self.request.GET.getlist('categories')
        if categories:
            for category in categories:
                category_q |= Q(product__category__name=category)
        colors = self.request.GET.getlist('colors')
        if colors:
            for color in colors:
                color_q |= Q(product__color__name=color)
        return brand_q & size_q & category_q & color_q

    def get_ordering(self) -> str | None:
        print(type(self.request))
        return get_ordering_from_request(self.request)

    def get_gender_filter(self) -> dict[str: str]:
        gender_variations = {
            '/shop/women/': {'product__gender__name': 'Women'},
            '/shop/men/': {'product__gender__name': 'Men'},
        }
        gender_filter = gender_variations.get(self.request.path, {})
        return gender_filter

    def get_queryset(self) -> QuerySet[ProductImage]:
        return get_filtered_products(self.get_filters(), self.get_ordering(), self.get_gender_filter())

    def get_context_data(self, *, object_list=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['ordering_options'] = get_ordering_option()
        context['brands_list'] = get_all_brands()
        context['sizes_list'] = get_all_sizes()
        context['categories_list'] = get_all_categories()
        context['colors_list'] = get_all_colors()
        context['selected_ordering'] = self.request.GET.get('ordering', '')
        context['selected_brands'] = self.request.GET.getlist('brands')
        context['selected_sizes'] = [int(size) for size in self.request.GET.getlist('sizes')]
        context['selected_categories'] = self.request.GET.getlist('categories')
        context['selected_colors'] = self.request.GET.getlist('colors')
        context['page_if_for_men_shoes'] = True if 'men' in self.request.path else False
        context['page_if_for_women_shoes'] = True if 'women' in self.request.path else False
        return context


class SearchView(ShopView):
    def get_queryset(self) -> QuerySet[ProductImage]:
        query = self.request.GET.get('q')
        search_vector = \
            SearchVector('product__name', weight='A') + \
            SearchVector('product__description', weight='B') + \
            SearchVector('product__name', weight='B') + \
            SearchVector('product__color__name', weight='C') + \
            SearchVector('product__brand__name', weight='C')
        search_query = SearchQuery(query)
        searched_queryset = get_queryset_after_search(super().get_queryset(), search_vector, search_query)
        return searched_queryset

    def get_context_data(self, *, object_list=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q')
        return context


class ProductView(generic.View):
    def get(self, request, *args, **kwargs) -> HttpResponse:
        view = ProductDetailView.as_view()
        print(type(view))
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs) -> HttpResponse:
        view = ProductFormView.as_view()
        return view(request, *args, **kwargs)


class ProductDetailView(generic.DetailView):
    model = Product
    template_name = "products/product-detail.html"
    context_object_name = "product"
    pk_url_kwarg = 'pk'

    def get_object(self, queryset=None) -> Product:
        if not hasattr(self, 'object'):
            self.object = super().get_object(queryset=queryset)
        return self.object

    def get_context_data(self, *, object_list=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        product_id = self.kwargs['pk']
        context["form"] = ReviewForm()
        context["product_images"] = get_single_product_images(product_id)
        context['product_sizes'] = get_single_product_sizes(product_id)
        context['product_reviews'] = get_single_product_reviews(product_id)
        context['reviews_quantity'] = get_single_product_reviews_quantity(product_id)
        context['average_rating'] = get_average_rating(product_id)
        ratings_count = get_ratings_count(product_id=product_id, reviews_quantity=context['reviews_quantity'])
        for rating_count in ratings_count:
            context[f'count_of_{rating_count["rate"]}_star_reviews'] = rating_count['count']
            context[f'percentage_of_{rating_count["rate"]}_star_reviews'] = rating_count['percent']
        context['product_gender'] = self.get_object().gender.name
        return context


class ProductFormView(generic.FormView):
    model = Product
    template_name = "products/product-detail.html"
    form_class = ReviewForm

    def post(self, request, *args, **kwargs) -> HttpResponse:
        if self.request.user.is_anonymous:
            return redirect('accounts:login')
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form: ReviewForm) -> HttpResponseRedirect:
        product = get_single_product(self.kwargs['pk'])
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

    def get_success_url(self) -> str:
        return reverse('products:home')


class ContactView(generic.FormView):
    template_name = "products/contact.html"
    form_class = ContactForm

    def form_valid(self, form) -> HttpResponseRedirect:
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        sender = form.cleaned_data['email']
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']

        tasks.send_email_from_contact_form.delay(first_name, last_name, sender, subject, message)
        return super(ContactView, self).form_valid(form)

    def get_success_url(self) -> str:
        return reverse('products:home')


class AboutView(generic.TemplateView):
    template_name = "products/about.html"
