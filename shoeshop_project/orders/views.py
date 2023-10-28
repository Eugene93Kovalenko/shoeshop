from decimal import Decimal

import stripe
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from accounts.models import CustomUser
from orders.cart import Cart
from orders.forms import CheckoutForm
from orders.models import *


class CartView(generic.ListView):
    template_name = "orders/cart.html"
    context_object_name = 'cart_items'

    def get_queryset(self):
        return Cart(self.request)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['recently_viewed'] = Product.objects.filter(slug__in=self.request.session[
            'recently_viewed']).order_by('-last_visit')[:4]
        return context


@require_POST
def add_to_cart(request, slug):
    cart = Cart(request)
    if request.POST.get('quantity') == '0' or not request.POST.get('product-size'):
        messages.warning(request, "Вы должны выбрать размер и количество товара")
        return redirect(request.META.get('HTTP_REFERER'))
    quantity = int(request.POST.get('quantity'))
    size = request.POST.get('product-size')
    product_variation = get_object_or_404(ProductVariation, product__slug=slug, size__name=size)
    if product_variation.quantity < quantity:
        messages.warning(request, "На складе нет этого товара в таком количестве")
        return redirect(request.META.get('HTTP_REFERER'))
    cart.add(product_variation=product_variation, quantity=quantity, user=request.user.username)
    return redirect("orders:cart")


def remove_from_cart(request, slug):
    cart = Cart(request)
    if request.method == 'POST':
        size = request.POST.get('size')
        product_variation = get_object_or_404(ProductVariation, product__slug=slug, size__name=size)
        cart.delete(product_variation=product_variation)
        return redirect("orders:cart")


class CheckoutFormView(generic.FormView):
    template_name = "orders/checkout.html"
    form_class = CheckoutForm

    def get_success_url(self):
        return reverse('orders:create-checkout-session')

    def form_valid(self, form):
        user = self.request.user
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.phone = form.cleaned_data['phone']
        user.save()
        if ShippingAddress.objects.get(user=user):
            ShippingAddress.objects.update(
                user=user,
                country=form.cleaned_data['country'],
                region=form.cleaned_data['region'],
                city=form.cleaned_data['city'],
                zip=form.cleaned_data['zip'],
                address=form.cleaned_data['address'],
                default=True
            )
        else:
            ShippingAddress.objects.create(
                user=user,
                country=form.cleaned_data['country'],
                region=form.cleaned_data['region'],
                city=form.cleaned_data['city'],
                zip=form.cleaned_data['zip'],
                address=form.cleaned_data['address'],
                default=True
            )
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
            customer_email=self.get_user_email()
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
        return line_items_list

    def get_user_email(self):
        # if self.request.user.is_authenticated:
        return self.request.user.email


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
            print("Payment successful")
            session = stripe.checkout.Session.retrieve(
                event['data']['object']['id'],
                expand=['line_items'],
            )
            _handle_successful_payment(session)
        return HttpResponse(status=200)


def _handle_successful_payment(session):
    user_id = session['client_reference_id']
    user = CustomUser.objects.get(id=user_id)
    amount = session['amount_total']
    ordered_date = timezone.now()
    order = Order.objects.create(
        user=user,
        ordered_date=ordered_date,
        ordered=True)
    for key, value in session['metadata'].items():
        order_item = OrderItem.objects.create(
            user=user,
            product_variation=ProductVariation.objects.get(id=key),
            quantity=value,
            ordered=True
        )
        order.products.add(order_item)
    Payment.objects.create(
        stripe_charge_id=session['id'],
        user=user,
        order=order,
        amount=amount / 100,
    )


class OrderCompleteView(generic.TemplateView):
    template_name = "orders/order-complete.html"

    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        cart.clear()
        context = super().get_context_data(**kwargs)
        return self.render_to_response(context)


class CancelView(generic.TemplateView):
    template_name = "orders/cancel.html"
