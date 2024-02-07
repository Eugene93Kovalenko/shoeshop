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
from django.views.generic.edit import FormMixin

from accounts.models import CustomUser
from orders.cart import Cart
from orders.forms import CheckoutForm
from orders.models import *
from orders.tasks import send_order_conformation_mail


class CartView(generic.ListView):
    template_name = "orders/cart.html"
    context_object_name = 'cart_items'

    def get_queryset(self):
        return Cart(self.request)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        if self.request.session.get('recently_viewed'):
            context['recently_viewed'] = Product.objects.filter(slug__in=self.request.session[
                'recently_viewed']).order_by('-last_visit')[:4]
        # context['massage'] = messages.warning(self.request, "Вы не добавили ни одного товара в корзину")
        return context


# class CartView(generic.View):
#     def get(self, request, *args, **kwargs):
#         view = CartListView.as_view()
#         return view(request, *args, **kwargs)

    # def post(self, request, *args, **kwargs):
    #     view = CartCouponFormView.as_view()
    #     return view(request, *args, **kwargs)


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
        cart = Cart(self.request)
        ordered_date = timezone.now()
        old_order = Order.objects.filter(user=user, ordered=False)
        if old_order:
            Order.objects.get(user=user, ordered=False).delete()

            old_order_items = OrderItem.objects.filter(user=user, ordered=False)
            for item in old_order_items:
                item.delete()

        order = Order.objects.create(
            user=user,
            ordered_date=ordered_date,
            ordered=False)
        for item in cart:
            order_item = OrderItem.objects.create(
                user=user,
                product_variation=item['product_variation'],
                quantity=item['quantity']
            )
            order.products.add(order_item)
        old_shipping_address = ShippingAddress.objects.filter(user=user)
        if old_shipping_address:
            ShippingAddress.objects.get(user=user).delete()
        shipping_address = ShippingAddress.objects.create(
            user=user,
            country=form.cleaned_data['country'],
            region=form.cleaned_data['region'],
            city=form.cleaned_data['city'],
            zip=form.cleaned_data['zip'],
            address=form.cleaned_data['address'],
            default=True
        )
        order.shipping_address = shipping_address
        order.save()

        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.phone = form.cleaned_data['phone']
        user.save()
        return super(CheckoutFormView, self).form_valid(form)


# def get_coupon(request, code):
#     try:
#         coupon = Coupon.objects.get(code=code)
#         return coupon
#     except ObjectDoesNotExist:
#         messages.info(request, "This coupon does not exist")
#         return redirect("orders:cart")


# class AddCouponView(generic.View):
#     def post(self, *args, **kwargs):
#         form = CouponForm(self.request.POST or None)
#         if form.is_valid():
#             try:
#                 code = form.cleaned_data.get('code')
#                 order = Order.objects.get(
#                     user=self.request.user, ordered=False)
#                 order.coupon = get_coupon(self.request, code)
#                 order.save()
#                 return redirect("orders:cart")
#             except ObjectDoesNotExist:
#                 return redirect("orders:cart")


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

    def get_user_email(self):
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
    user_email = session['customer_details']['email']
    user_name = session['customer_details']['name']
    user = CustomUser.objects.get(id=user_id)
    amount = session['amount_total']
    ordered_date = timezone.now()
    order_item = OrderItem.objects.filter(
        user=user,
        ordered=False)
    order_item.update(ordered=True)
    order = Order.objects.filter(
        user=user,
        ordered=False)
    Payment.objects.create(
        stripe_charge_id=session['id'],
        user=user,
        order=order[0],
        amount=amount / 100,
    )
    order.update(
        ordered_date=ordered_date,
        ordered=True)

    send_order_conformation_mail.delay(user_name, user_email)


class OrderCompleteView(generic.TemplateView):
    template_name = "orders/order-complete.html"

    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        cart.clear()
        context = super().get_context_data(**kwargs)
        return self.render_to_response(context)


class CancelView(generic.TemplateView):
    template_name = "orders/cancel.html"
