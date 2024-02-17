from django.urls import path

from .views import *

app_name = 'orders'

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    # path('add_to_cart/<slug:slug>', add_to_cart, name='add-to-cart'),
    path('add_to_cart/<slug:slug>', AddToCart.as_view(), name='add-to-cart'),
    # path('remove_from_cart/<slug:slug>', remove_from_cart, name='remove-from-cart'),
    path('remove_from_cart/<slug:slug>', RemoveFromCart.as_view(), name='remove-from-cart'),
    path('cart/checkout/', CheckoutFormView.as_view(), name='checkout'),
    path("create_checkout_session/", CreateStripeCheckoutSessionView.as_view(), name="create-checkout-session"),
    path('success/', OrderCompleteView.as_view(), name='success'),
    path('cancel/', CancelView.as_view(), name='cancel'),
    path("webhooks/stripe/", StripeWebhookView.as_view(), name="stripe-webhook"),
]
