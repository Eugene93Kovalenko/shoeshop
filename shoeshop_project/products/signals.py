from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django_tools.middlewares import ThreadLocal

from orders.cart import Cart
from products.models import Product


@receiver(pre_save, sender=Product)
def update_actual_price(sender, instance, **kwargs):
    if instance.discount:
        instance.actual_price = round(instance.price - ((instance.price * instance.discount) / 100), 2)
    else:
        instance.actual_price = instance.price

    # todo вынести в отдельный сигнал?
    request = ThreadLocal.get_current_request()
    cart = Cart(request)
    cart.update_price(instance)


