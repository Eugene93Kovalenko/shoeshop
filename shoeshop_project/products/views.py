# from datetime import datetime
# from time import timezone
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Avg
from django.shortcuts import get_object_or_404, redirect
from django.views import generic
from django.core.mail import send_mail
from django.views.generic.edit import FormMixin

from .forms import ContactForm, ReviewForm
from .models import *


class HomeView(generic.ListView):
    model = Product
    template_name = "products/index.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.all()[:16]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ShopView(generic.ListView):
    model = Product
    template_name = "products/shop.html"
    context_object_name = "products"
    paginate_by = 2

    def get_filters(self):
        brand_q, size_q, category_q, color_q, material_q = Q(), Q(), Q(), Q(), Q()

        if self.request.GET.getlist('brand'):
            for brand in self.request.GET.getlist('brand'):
                brand_q |= Q(brand__name=brand)

        if self.request.GET.getlist('sizes'):
            for size in self.request.GET.getlist('sizes'):
                size_q |= Q(product_variation__size__name=size)

        if self.request.GET.getlist('category'):
            for category in self.request.GET.getlist('category'):
                category_q |= Q(category__name=category)

        if self.request.GET.getlist('color'):
            for color in self.request.GET.getlist('color'):
                color_q |= Q(color__name=color)

        if self.request.GET.getlist('material'):
            for material in self.request.GET.getlist('material'):
                material_q |= Q(material__name=material)

        return brand_q & size_q & category_q & color_q & material_q

    def get_ordering(self):
        return self.request.GET.get('ordering')

    def get_queryset(self):
        gender_filters = {
            '/shop/women/': {'gender__name': 'Women'},
            '/shop/men/': {'gender__name': 'Men'},
        }
        gender_filter = gender_filters.get(self.request.path, {})
        if self.get_ordering():
            return Product.objects.filter(self.get_filters(), **gender_filter).order_by(self.get_ordering()).distinct()
        else:
            return Product.objects.filter(self.get_filters(), **gender_filter).distinct()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brands_list'] = Brand.objects.all()
        context['sizes_list'] = Size.objects.all()
        context['categories_list'] = Category.objects.all()
        context['colors_list'] = Color.objects.all()
        context['materials_list'] = Material.objects.all()
        context['genders_list'] = Gender.objects.all().exclude(name='Unisex').order_by('name')
        context['selected_ordering'] = self.request.GET.get('ordering')
        context['selected_brand'] = [brand for brand in self.request.GET.getlist('brand')]
        context['selected_size'] = [int(size) for size in self.request.GET.getlist('size')]
        context['selected_category'] = [brand for brand in self.request.GET.getlist('category')]
        context['selected_color'] = [brand for brand in self.request.GET.getlist('color')]
        context['selected_material'] = [brand for brand in self.request.GET.getlist('material')]
        context['ordering_options'] = Product.ORDERING_OPTIONS
        return context


class ProductDetailView(FormMixin, generic.DetailView):
    model = Product
    template_name = "products/product-detail.html"
    context_object_name = "product"
    slug_url_kwarg = "product_slug"
    form_class = ReviewForm

    # def get_initial(self):
    #     return self.get_object()

    def get(self, request, *args, **kwargs):
        if 'recently_viewed' not in request.session:
            request.session['recently_viewed'] = [self.kwargs['product_slug']]
        else:
            if self.kwargs['product_slug'] in request.session['recently_viewed']:
                request.session['recently_viewed'].remove(self.kwargs['product_slug'])
            request.session['recently_viewed'].insert(0, self.kwargs['product_slug'])

        request.session.modified = True
        current_product = Product.objects.get(slug=self.kwargs["product_slug"])
        current_product.last_visit = timezone.now()
        current_product.save()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_anonymous:
            return redirect('accounts:login')
        # self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        product = Product.objects.get(slug=self.kwargs["product_slug"])
        user = self.request.user
        form_data = form.cleaned_data
        review = Review.objects.create(product=product,
                                       rate=form_data['rate'],
                                       text=form_data['text'],
                                       user=user,
                                       first_name=form_data['first_name'],
                                       last_name=form_data['last_name'])
        review.save()
        return super(ProductDetailView, self).form_valid(form)

    def get_success_url(self):
        return reverse('products:home')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_images"] = ProductImage.objects.filter(product__slug=self.kwargs["product_slug"])
        context['sizes_per_product_list'] = [product.size for product in ProductVariation.objects.filter(
            product__slug=self.kwargs["product_slug"])]
        context['product_reviews'] = Review.objects.filter(product__slug=self.kwargs["product_slug"])
        context['reviews_quantity'] = Review.objects.filter(product__slug=self.kwargs["product_slug"]).count()
        context['average_rating'] = self.get_average_rating()
        return context

    def _round_custom(self, num, step):
        return round(num / step) * step

    def get_average_rating(self):
        average_product_rating = Review.objects.filter(product__slug=self.kwargs[
            "product_slug"]).aggregate(average=Avg('rate', default=0))
        if average_product_rating is not None:
            context = self._round_custom(float(average_product_rating['average']), 0.5)
        return context


class ContactView(generic.FormView):
    template_name = "products/contact.html"
    form_class = ContactForm

    def get_success_url(self):
        return reverse('products:home')

    def form_valid(self, form):
        sender = form.cleaned_data['email']
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        send_mail(
            subject=subject,
            message=message,
            from_email=sender,
            recipient_list=['udjin93@yandex.ru'],
        )
        return super(ContactView, self).form_valid(form)


class AboutView(generic.TemplateView):
    template_name = "products/about.html"


class ProductReview(generic.ListView):
    model = Product
    template_name = "products/product-detail.html"
    context_object_name = "reviews"

    def get_queryset(self):
        print(Review.objects.filter(product__slug='women_boots'))
        return Review.objects.filter(product__slug='women_boots')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews_quantity'] = Review.objects.filter(product__slug='women_boots').count()
        return context
