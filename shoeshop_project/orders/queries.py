import logging

from django.shortcuts import get_object_or_404
from django.utils import timezone

from accounts.models import CustomUser
from orders.models import Payment, OrderItem, Order, ShippingAddress
from products.models import Product, ProductVariation


logger = logging.getLogger('main')

def get_recently_viewed_products(session):
    return Product.objects.filter(slug__in=session).order_by('-last_visit')[:4]


def get_custom_user(user_id):
    return CustomUser.objects.get(id=user_id)


def update_product_purchases_count_and_quantity_in_stock(order):
    items = order.products.all()
    for item in items:
        quantity = item.quantity

        item.product_variation.quantity -= quantity
        item.product_variation.save()

        item.product_variation.product.purchases_count += quantity
        item.product_variation.product.save()


def create_order_item(user, product_variation, quantity):
    return OrderItem.objects.create(user=user, product_variation=product_variation, quantity=quantity)


def create_order(user):
    order_datetime = timezone.now()
    return Order.objects.create(user=user, ordered_datetime=order_datetime, ordered=False)


def create_payment(session_id, user, order, amount):
    Payment.objects.create(
        stripe_charge_id=session_id,
        user=user,
        order=order,
        amount=amount / 100,
    )


def get_product_variation(slug, size):
    return get_object_or_404(ProductVariation, product__slug=slug, size__name=size)


def get_order_items(user):
    return OrderItem.objects.filter(user=user, ordered=False)


def update_order_items(user):
    return get_order_items(user).update(ordered=True)


def get_order(user):
    try:
        return Order.objects.get(user=user, ordered=False)
    except Order.DoesNotExist:
        return None
    except Order.MultipleObjectsReturned:
        logger.error('Multiple objects returned. There should be only 1 order per user with field ordered=False')
        return None


def get_shipping_address(user):
    try:
        return ShippingAddress.objects.get(user=user)
    except Order.DoesNotExist:
        return None
    except Order.MultipleObjectsReturned:
        logger.error('Multiple objects returned. There should be only 1 shipping address per user')
        return None


def create_shipping_address(user, form):
    return ShippingAddress.objects.create(
        user=user,
        country=form.cleaned_data['country'],
        region=form.cleaned_data['region'],
        city=form.cleaned_data['city'],
        zip=form.cleaned_data['zip'],
        address=form.cleaned_data['address'],
        default=True
    )


def update_order(order):
    ordered_datetime = timezone.now()
    order.ordered_datetime = ordered_datetime
    order.ordered = True
    order.save()


def delete_existing_order(user):
    existing_order = get_order(user)
    if existing_order:
        existing_order.delete()
        existing_order_items = get_order_items(user)
        for item in existing_order_items:
            item.delete()


def add_order_items_to_order(cart, order, user):
    for item in cart:
        order_item = create_order_item(user, item['product_variation'], item['quantity'])
        order.products.add(order_item)


def delete_existing_shipping_address(user):
    existing_shipping_address = get_shipping_address(user)
    if existing_shipping_address:
        existing_shipping_address.delete()


def create_new_shipping_address(user, form, order):
    new_shipping_address = create_shipping_address(user, form)
    order.shipping_address = new_shipping_address
    order.save()


def update_user_info(user, form):
    user.first_name = form.cleaned_data['first_name']
    user.last_name = form.cleaned_data['last_name']
    user.phone = form.cleaned_data['phone']
    user.save()

