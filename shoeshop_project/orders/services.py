from decimal import Decimal

from django.db import transaction
from django_tools.middlewares import ThreadLocal

from orders.cart import Cart
from . import tasks
from .queries import update_product_purchases_count_and_quantity_in_stock, create_payment, get_custom_user, \
    update_order_items, update_order, get_order


def get_metadata(request):
    cart = Cart(request)
    metadata = {}
    for item in cart:
        metadata[item['product_variation_id']] = item['quantity']
    return metadata


def get_line_items_list(request):
    cart = Cart(request)
    line_items_list = []
    for item in cart:
        line_items_list.append(
            {
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(Decimal(item['price'])) * 100,
                    'product_data': {
                        'name': item['product_name'],
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


@transaction.atomic
def handle_successful_payment(session):
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
