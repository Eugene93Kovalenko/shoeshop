from time import timezone

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from orders.models import OrderItem, Order
from .filters import ProductFilter
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
        brand_q, size_q, category_q, color_q, material_q, style_q = Q(), Q(), Q(), Q(), Q(), Q()

        for brand in self.request.GET.getlist('brand'):
            if brand:
                brand_q |= Q(brand__name=brand)

        for size in self.request.GET.getlist('size'):
            if size:
                size_q |= Q(product_variation__size__name=size)

        for category in self.request.GET.getlist('category'):
            if category:
                category_q |= Q(category__name=category)

        for color in self.request.GET.getlist('color'):
            if color:
                color_q |= Q(color__name=color)

        for material in self.request.GET.getlist('material'):
            if material:
                material_q |= Q(material__name=material)

        for style in self.request.GET.getlist('style'):
            if style:
                style_q |= Q(style__name=style)
        return brand_q & size_q & category_q & color_q & material_q & style_q

    def get_urlencode_for_ordering(self):
        urlencode = self.request.GET.urlencode()
        if 'ordering' in urlencode:
            if urlencode.count('=') == 1:
                urlencode = ''
            else:
                urlencode = urlencode[urlencode.find('&') + 1:]
        return urlencode

    def get_ordering(self):
        return self.request.GET.get('ordering')

    def get_queryset(self):
        if self.request.GET.get("ordering"):
            # if self.request.path == '/shop/men/':
            #     return Product.objects.filter(self.get_filters(), gender__name='Men')
            # elif self.request.path == '/shop/women/':
            #     return Product.objects.filter(self.get_filters(), gender__name='Women')
            return Product.objects.filter(self.get_filters()).order_by(self.get_ordering())
        return Product.objects.filter(self.get_filters())

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brands_list'] = Brand.objects.all()
        context['sizes_list'] = Size.objects.all()
        context['categories_list'] = Category.objects.all()
        context['colors_list'] = Color.objects.all()
        context['materials_list'] = Material.objects.all()
        context['stiles_list'] = Style.objects.all()
        context['genders_list'] = Gender.objects.all().exclude(name='Unisex').order_by('name')
        context['selected_size'] = [int(size) for size in self.request.GET.getlist('size')]
        context['selected_brand'] = [brand for brand in self.request.GET.getlist('brand')]
        context['selected_ordering'] = self.request.GET.get('ordering')
        context['ordering_options'] = [
            ('Popularity', 'num_visits'), ('Last', '-created_at'), ('Price high first', 'price'),
            ('Price low first', '-price')
        ]
        context['url'] = self.get_urlencode_for_ordering()
        return context


class ProductDetailView(generic.DetailView):
    model = Product
    template_name = "products/product-detail.html"
    context_object_name = "product"
    slug_url_kwarg = "product_slug"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_images"] = ProductImage.objects.filter(product__slug=self.kwargs["product_slug"])
        context['sizes_per_product_list'] = [product.size for product in ProductVariation.objects.filter(
            product__slug=self.kwargs["product_slug"])]
        return context


class AboutView(generic.TemplateView):
    template_name = "products/about.html"


class ContactView(generic.TemplateView):
    template_name = "products/contact.html"
