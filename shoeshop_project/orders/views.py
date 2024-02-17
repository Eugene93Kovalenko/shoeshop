import time
from decimal import Decimal

import stripe
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic.detail import SingleObjectMixin

from accounts.models import CustomUser
from orders.cart import Cart
from orders.forms import CheckoutForm
from orders.models import *
from . import tasks
from .queries import update_product_purchases_count_and_quantity_in_stock, create_payment, get_custom_user, \
    update_order_items, update_order, get_order, get_recently_viewed_products, get_order_items, get_product_variation, \
    create_order, create_order_item, get_shipping_address, create_shipping_address


class CartView(generic.ListView):
    template_name = "orders/cart.html"
    context_object_name = 'cart_items'

    def get_queryset(self):
        return Cart(self.request)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        if self.request.session.get('recently_viewed'):
            context['recently_viewed'] = get_recently_viewed_products(self.request.session['recently_viewed'])
        # context['massage'] = messages.warning(self.request, "Вы не добавили ни одного товара в корзину")
        return context


@require_POST
def add_to_cart(request, slug):
    cart = Cart(request)
    if request.POST.get('quantity') == '0' or not request.POST.get('product-size'):
        messages.warning(request, "You have to choose product size and quantity")
        return redirect(request.META.get('HTTP_REFERER'))
    quantity = int(request.POST.get('quantity'))
    size = request.POST.get('product-size')
    product_variation = get_product_variation(slug, size)
    if product_variation.quantity < quantity:
        messages.warning(request, "This product is not in stock in this quantity")
        return redirect(request.META.get('HTTP_REFERER'))
    cart.add(product_variation=product_variation, quantity=quantity, user=request.user.username)
    return redirect("orders:cart")


@require_POST
def remove_from_cart(request, slug):
    cart = Cart(request)
    size = request.POST.get('size')
    product_variation = get_product_variation(slug, size)
    cart.delete(product_variation)
    return redirect("orders:cart")


class CheckoutFormView(generic.FormView):
    template_name = "orders/checkout.html"
    form_class = CheckoutForm

    def get_success_url(self):
        return reverse('orders:create-checkout-session')

    def form_valid(self, form):
        cart = Cart(self.request)
        user = self.request.user
        existing_order = get_order(user)
        if existing_order:
            existing_order.delete()
            existing_order_items = get_order_items(user)
            for item in existing_order_items:
                item.delete()
        new_order = create_order(user)
        for item in cart:
            order_item = create_order_item(user, item['product_variation'], item['quantity'])
            new_order.products.add(order_item)
        existing_shipping_address = get_shipping_address(user)
        if existing_shipping_address:
            existing_shipping_address.delete()
        new_shipping_address = create_shipping_address(user, form)
        new_order.shipping_address = new_shipping_address
        new_order.save()

        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.phone = form.cleaned_data['phone']
        user.save()
        return super(CheckoutFormView, self).form_valid(form)


class CreateStripeCheckoutSessionView(generic.View):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    def get(self, request):
        checkout_session = stripe.checkout.Session.create(
            client_reference_id=request.user.id,
            payment_method_types=['card'],
            line_items=self.get_line_items_list(),
            mode='payment',
            metadata=self.get_metadata(),
            success_url=settings.PAYMENT_SUCCESS_URL,
            cancel_url=settings.PAYMENT_CANCEL_URL,
            # customer_email=self.get_user_email()
        )
        return redirect(checkout_session.url)

    def get_metadata(self):
        cart = Cart(self.request)
        metadata = {}
        for item in cart:
            metadata[item['product_variation'].id] = item['quantity']
        return metadata

    def get_line_items_list(self):
        cart = Cart(self.request)
        line_items_list = []
        for item in cart:
            line_items_list.append(
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(item['price']) * 100,
                        'product_data': {
                            'name': item['product_variation'].product.name,
                        },
                    },
                    'quantity': item['quantity']
                }
            )
        line_items_list.append(
            {
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(cart.get_delivery_price()) * 100,
                    'product_data': {
                        'name': 'DELIVERY',
                    },
                },
                'quantity': '1'
            }
        )
        return line_items_list


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(generic.View):
    @staticmethod
    def post(request):
        payload = request.body
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)

        if event["type"] == "checkout.session.completed":
            session = stripe.checkout.Session.retrieve(
                event['data']['object']['id'],
                expand=['line_items'],
            )
            _handle_successful_payment(session)
        return HttpResponse(status=200)


# todo atomic
def _handle_successful_payment(session):
    user_id = session['client_reference_id']
    user_email = session['customer_details']['email']
    user_name = session['customer_details']['name']
    amount = session['amount_total']
    user = get_custom_user(user_id)
    update_order_items(user)
    order = get_order(user)
    update_product_purchases_count_and_quantity_in_stock(order)
    update_order(order)
    create_payment(session['id'], user, order, amount)
    tasks.send_order_conformation_mail.delay(user_name, user_email)


class OrderCompleteView(generic.TemplateView):
    template_name = "orders/order-complete.html"

    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        cart.clear()
        context = super().get_context_data(**kwargs)
        return self.render_to_response(context)


class CancelView(generic.TemplateView):
    template_name = "orders/cancel.html"
