import stripe
import logging
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from orders.cart import Cart
from orders.forms import CheckoutForm
from orders.models import *
from .queries import \
    get_order, \
    get_recently_viewed_products, \
    get_order_items, \
    get_product_variation, \
    create_order, \
    create_order_item, \
    get_shipping_address, \
    create_shipping_address, delete_existing_order, add_order_items_in_order, delete_existing_shipping_address, \
    update_user_info
from .services import get_metadata, get_line_items_list, handle_successful_payment


logger = logging.getLogger('main')


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
        return context


class AddToCart(generic.View):
    def post(self, request, slug):
        if request.POST.get('quantity') == '0' or not request.POST.get('product-size'):
            messages.warning(request, "You have to choose product size and quantity")
            return redirect(request.META.get('HTTP_REFERER'))
        cart = Cart(self.request)
        quantity = int(request.POST.get('quantity'))
        size = request.POST.get('product-size')
        product_variation = get_product_variation(slug, size)
        if product_variation.quantity < quantity:
            messages.warning(request, "This product is not in stock in this quantity")
            return redirect(request.META.get('HTTP_REFERER'))
        cart.add(product_variation=product_variation, quantity=quantity, user=self.request.user.email)
        return redirect("orders:cart")


class RemoveFromCart(generic.View):
    def post(self, request, slug):
        cart = Cart(self.request)
        size = request.POST.get('size')
        product_variation = get_product_variation(slug, size)
        cart.delete(product_variation)
        logger.info(f'{product_variation} удален из корзины')
        return redirect("orders:cart")


class CheckoutFormView(generic.FormView):
    template_name = "orders/checkout.html"
    form_class = CheckoutForm

    def get_success_url(self):
        return reverse('orders:create-checkout-session')

    def form_valid(self, form):
        cart = Cart(self.request)
        user = self.request.user

        delete_existing_order(user)
        new_order = create_order(user)
        add_order_items_in_order(cart, new_order, user)

        delete_existing_shipping_address(user)
        new_shipping_address = create_shipping_address(user, form)
        new_order.shipping_address = new_shipping_address
        new_order.save()

        update_user_info(user, form)
        return super(CheckoutFormView, self).form_valid(form)


class CreateStripeCheckoutSessionView(generic.View):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    def get(self, request):
        checkout_session = stripe.checkout.Session.create(
            client_reference_id=request.user.id,
            payment_method_types=['card'],
            line_items=get_line_items_list(self.request),
            mode='payment',
            metadata=get_metadata(self.request),
            success_url=settings.PAYMENT_SUCCESS_URL,
            cancel_url=settings.PAYMENT_CANCEL_URL,
        )
        # todo редиректить на прпомежуточную вьюху?
        return redirect(checkout_session.url)


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
            handle_successful_payment(session)
        return HttpResponse(status=200)


class OrderCompleteView(generic.TemplateView):
    template_name = "orders/order-complete.html"

    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        cart.clear()
        context = super().get_context_data(**kwargs)
        return self.render_to_response(context)


class CancelView(generic.TemplateView):
    template_name = "orders/cancel.html"
