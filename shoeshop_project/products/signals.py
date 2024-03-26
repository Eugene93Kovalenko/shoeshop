from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django_tools.middlewares import ThreadLocal

from orders.cart import Cart
from products.models import Product


@receiver(pre_save, sender=Product)
def update_actual_price(sender, instance: Product, **kwargs) -> None:
    if instance.discount:
        instance.actual_price = round(instance.price - ((instance.price * instance.discount) / 100), 2)
    else:
        instance.actual_price = instance.price


@receiver(post_save, sender=Product)
def update_actual_price_in_cart(sender, instance: Product, **kwargs) -> None:
    request = ThreadLocal.get_current_request()
    cart = Cart(request)
    cart.update_price(instance)

