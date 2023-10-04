from django.urls import path

from .views import *

app_name = 'orders'

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    # path('cart/', cart_v, name='cart'),
    # path('add_to_cart/<slug:slug>', add_to_cart, name='add-to-cart'),
    path('add_to_cart/<slug:slug>', cart_add, name='add-to-cart'),
    path('remove_from_cart/<slug:slug>', cart_delete, name='remove-from-cart'),
    path('cart/checkout/', CheckoutView.as_view(), name='checkout'),
    path('cart/checkout/payment', PaymentView.as_view(), name='payment'),
    path('order_complete/', OrderCompleteView.as_view(), name='order-complete'),
]
