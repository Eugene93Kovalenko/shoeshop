from django.utils import timezone

from accounts.models import CustomUser
from orders.models import Payment, OrderItem, Order
from products.models import Product


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


def create_payment(session_id, user, order, amount):
    Payment.objects.create(
        stripe_charge_id=session_id,
        user=user,
        order=order,
        amount=amount / 100,
    )


def get_order_items(user):
    return OrderItem.objects.filter(user=user, ordered=False)


def update_order_items(user):
    return get_order_items(user).update(ordered=True)


def get_order(user):
    try:
        return Order.objects.get(user=user, ordered=False)
    except Order.DoesNotExist:
        return None


# def delete_order(user):
#     return get_order(user).delete()


def update_order(order):
    ordered_datetime = timezone.now()
    order.ordered_datetime = ordered_datetime
    order.ordered = True
    order.save()

