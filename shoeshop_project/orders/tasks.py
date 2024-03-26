from __future__ import absolute_import, unicode_literals

from datetime import timedelta

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

from orders.models import Order


@shared_task()
def send_order_conformation_mail(user_name: str, user_email: str) -> None:
    body = f"""
        Hi {user_name}!\n\n
        Thank you for your purchase!\n\n
    """
    send_mail('ShoeShop purchase', body, None, [user_email], fail_silently=False)


@shared_task()
def send_email_with_orders_count_made_yesterday() -> None:
    yesterday = timezone.now() - timedelta(days=1)
    start_of_yesterday = timezone.make_aware(timezone.datetime.combine(yesterday.date(), timezone.datetime.min.time()))
    end_of_yesterday = timezone.make_aware(timezone.datetime.combine(yesterday.date(), timezone.datetime.max.time()))
    orders_count = Order.objects.filter(ordered_datetime__gte=start_of_yesterday, ordered_datetime__lt=end_of_yesterday,
                                        ordered=True).count()
    body = f"""
        You received {orders_count} orders yesterday.\n\n
    """
    send_mail(f'Orders placed {yesterday}', body, None, ['keugenemail@gmail.com'], fail_silently=False)
