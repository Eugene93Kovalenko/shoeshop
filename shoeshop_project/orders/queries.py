import logging

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone

from accounts.models import CustomUser
from orders.cart import Cart
from orders.forms import CheckoutForm
from orders.models import Payment, OrderItem, Order, ShippingAddress
from products.models import ProductVariation, ProductImage

logger = logging.getLogger('main')


def get_new_products(cart_session: Cart) -> QuerySet[ProductImage]:
    product_ids_in_cart = [product['product_id'] for product in cart_session]
    return ProductImage.objects.select_related('product'). \
                                filter(is_main=True). \
                                exclude(product__id__in=product_ids_in_cart). \
                                order_by('-product__created_at')[:4]


def get_custom_user(user_id: int) -> CustomUser:
    return CustomUser.objects.get(id=user_id)


def update_product_purchases_count_and_quantity_in_stock(order: Order) -> None:
    items = order.products.all()
    for item in items:
        quantity = item.quantity

        item.product_variation.quantity -= quantity
        item.product_variation.save()

        item.product_variation.product.purchases_count += quantity
        item.product_variation.product.save()


def create_order_item(user: CustomUser, product_variation_id: int, quantity: int) -> OrderItem:
    product_variation = ProductVariation.objects.get(id=product_variation_id)
    order_item = OrderItem.objects.create(
        user=user,
        product_variation=product_variation,
        quantity=quantity
    )
    return order_item


def create_order(user: CustomUser) -> Order:
    order_datetime = timezone.now()
    order = Order.objects.create(
        user=user,
        ordered_datetime=order_datetime,
        ordered=False
    )
    return order


def create_payment(session_id: str, user: CustomUser, order: Order, amount: int) -> None:
    Payment.objects.create(
        stripe_charge_id=session_id,
        user=user,
        order=order,
        amount=amount / 100,
    )


def get_product_variation(product_id: str, size: str) -> ProductVariation | None:
    return get_object_or_404(ProductVariation, product__id=product_id, size__name=size)


def get_order_items(user: CustomUser) -> QuerySet[OrderItem]:
    return OrderItem.objects.filter(user=user, ordered=False)


def update_order_items(user: CustomUser):
    get_order_items(user).update(ordered=True)


def get_order(user: CustomUser) -> Order | None:
    try:
        return Order.objects.get(user=user, ordered=False)
    except Order.DoesNotExist:
        return None
    except Order.MultipleObjectsReturned:
        logger.error('Multiple objects returned. There should be only 1 order per user with field ordered=False')
        return None


def get_shipping_address(user: CustomUser) -> ShippingAddress | None:
    try:
        return ShippingAddress.objects.get(user=user)
    except ShippingAddress.DoesNotExist:
        return None
    except ShippingAddress.MultipleObjectsReturned:
        logger.error('Multiple objects returned. There should be only 1 shipping address per user')
        return None


def create_shipping_address(user: CustomUser, form: CheckoutForm) -> ShippingAddress:
    return ShippingAddress.objects.create(
        user=user,
        country=form.cleaned_data['country'],
        region=form.cleaned_data['region'],
        city=form.cleaned_data['city'],
        zip=form.cleaned_data['zip'],
        address=form.cleaned_data['address'],
        default=True
    )


def update_order(order: Order) -> None:
    ordered_datetime = timezone.now()
    order.ordered_datetime = ordered_datetime
    order.ordered = True
    order.save()


def delete_existing_order(user: CustomUser) -> None:
    existing_order = get_order(user)
    if existing_order:
        existing_order.delete()
        existing_order_items = get_order_items(user)
        for item in existing_order_items:
            item.delete()


def add_order_items_to_order(cart, order: Order, user: CustomUser) -> None:
    for item in cart:
        order_item = create_order_item(user, item['product_variation_id'], item['quantity'])
        order.products.add(order_item)


def delete_existing_shipping_address(user: CustomUser) -> None:
    existing_shipping_address = get_shipping_address(user)
    if existing_shipping_address:
        existing_shipping_address.delete()


def create_new_shipping_address(user: CustomUser, form: CheckoutForm, order: Order) -> None:
    new_shipping_address = create_shipping_address(user, form)
    order.shipping_address = new_shipping_address
    order.save()


def update_user_info(user: CustomUser, form: CheckoutForm) -> None:
    user.first_name = form.cleaned_data['first_name']
    user.last_name = form.cleaned_data['last_name']
    user.phone = form.cleaned_data['phone']
    user.save()
