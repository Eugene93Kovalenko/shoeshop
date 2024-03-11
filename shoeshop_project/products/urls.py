from django.urls import path

from .views import *

app_name = 'products'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('shop/men/', ShopView.as_view(), name='shop-men'),
    path('shop/women/', ShopView.as_view(), name='shop-women'),
    path('shop/', ShopView.as_view(), name='shop'),
    path('shop/<uuid:pk>', ProductView.as_view(), name='product-detail'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('shop/search/', SearchView.as_view(), name='search'),
]
