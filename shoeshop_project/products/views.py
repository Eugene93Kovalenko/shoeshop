# from datetime import datetime
# from time import timezone
import time

from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, SearchHeadline
from django.utils import timezone

from django.db.models import Q, Avg, Count, F, ExpressionWrapper, DecimalField
from django.shortcuts import get_object_or_404, redirect
from django.views import generic
from django.views.generic.detail import SingleObjectMixin

from .forms import ContactForm, ReviewForm
from .models import *
from . import tasks
from .queries import get_all_products, get_filtered_products, get_all_categories, get_all_sizes, get_all_brands, \
    get_all_colors, get_ordering_option, get_product_from_slug, get_single_product_images, \
    get_single_product_variations, get_single_product_reviews, get_single_product_reviews_quantity, \
    get_single_product_rating, create_product_review, get_ratings_count


class HomeView(generic.ListView):
    model = Product
    template_name = "products/index.html"
    context_object_name = "products"

    def get_queryset(self):
        return get_all_products()[:8]


class ShopView(generic.ListView):
    model = Product
    template_name = "products/shop.html"
    context_object_name = "products"
    paginate_by = 2

    def get_filters(self):
        brand_q, size_q, category_q, color_q = Q(), Q(), Q(), Q()

        if self.request.GET.getlist('brand'):
            for brand in self.request.GET.getlist('brand'):
                brand_q |= Q(brand__name=brand)
        if self.request.GET.getlist('size'):
            for size in self.request.GET.getlist('size'):
                size_q |= Q(product_variation__size__name=size)
        if self.request.GET.getlist('category'):
            for category in self.request.GET.getlist('category'):
                category_q |= Q(category__name=category)
        if self.request.GET.getlist('color'):
            for color in self.request.GET.getlist('color'):
                color_q |= Q(color__name=color)
        return brand_q & size_q & category_q & color_q

    def get_ordering(self):
        return self.request.GET.get('ordering', '')

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
        context['genders_list'] = Gender.objects.all().exclude(name='Unisex').order_by('name')
        context['selected_ordering'] = self.request.GET.get('ordering')
        context['selected_brand'] = [brand for brand in self.request.GET.getlist('brand')]
        context['selected_size'] = [int(size) for size in self.request.GET.getlist('size')]
        context['selected_category'] = [brand for brand in self.request.GET.getlist('category')]
        context['selected_color'] = [brand for brand in self.request.GET.getlist('color')]
        context['selected_search'] = self.request.GET.get('q')
        return context


class SearchView(ShopView):
    def get_queryset(self):
        query = self.request.GET.get("q")
        search_vector = SearchVector("name", "description")
        search_query = SearchQuery(query)
        if super().get_filters() or super().get_ordering():
            search_result = (
                super().get_queryset().annotate(
                    search=search_vector, rank=SearchRank(search_vector, search_query)
                )
                .filter(search=search_query)
            )
        else:
            search_result = (
                Product.objects.annotate(
                    search=search_vector, rank=SearchRank(search_vector, search_query)
                )
                .filter(search=search_query)
            )
        return search_result

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
        if 'recently_viewed' not in request.session:
            request.session['recently_viewed'] = [self.kwargs['product_slug']]
        else:
            if self.kwargs['product_slug'] in request.session['recently_viewed']:
                request.session['recently_viewed'].remove(self.kwargs['product_slug'])
            request.session['recently_viewed'].insert(0, self.kwargs['product_slug'])
            if len(request.session['recently_viewed']) > 4:
                request.session['recently_viewed'].pop()
        request.session.modified = True
        current_product = get_product_from_slug(self.kwargs["product_slug"])
        current_product.last_visit = timezone.now()
        current_product.save()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ReviewForm()
        context["product_images"] = get_single_product_images(self.kwargs["product_slug"])
        context['list_of_product_sizes'] = \
            [product.size for product in get_single_product_variations(self.kwargs["product_slug"])]
        context['product_reviews'] = get_single_product_reviews(self.kwargs["product_slug"])
        context['reviews_quantity'] = get_single_product_reviews_quantity(self.kwargs["product_slug"])
        context['average_rating'] = self.get_average_rating()
        ratings_count = get_ratings_count(self.kwargs["product_slug"])
        for rating_count in ratings_count:
            context[f'count_of_{rating_count["rate"]}_star_reviews'] = rating_count['count']
            context[f'percentage_of_{rating_count["rate"]}_star_reviews'] = rating_count['percent']
        return context

    # todo move to helpers?
    def round_int_custom(self, num, step):
        return round(num / step) * step

    def get_average_rating(self):
        average_product_rating = get_single_product_rating(self.kwargs["product_slug"])
        if not average_product_rating:
            return None
        return self.round_int_custom(float(average_product_rating['average']), 0.5)


class ProductFormView(SingleObjectMixin, generic.FormView):
    model = Product
    template_name = "products/product-detail.html"
    form_class = ReviewForm

    # todo: login required?
    def post(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_anonymous:
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

    def get_success_url(self):
        return reverse('products:home')

    def form_valid(self, form):
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        sender = form.cleaned_data['email']
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']

        tasks.send_email_from_contact_form.delay(first_name, last_name, sender, subject, message)
        return super(ContactView, self).form_valid(form)


class AboutView(generic.TemplateView):
    template_name = "products/about.html"
