from __future__ import absolute_import, unicode_literals

from celery import shared_task
from django.core.mail import send_mail


@shared_task()
def send_email_from_contact_form(first_name: str, last_name: str, sender: str, subject: str, message: str) -> None:
    body = f"""
        Name: {first_name} {last_name}.\n\n
        From email: {sender}\n\n
        Subject: {subject}\n\n
        Message: {message}\n\n
    """
    send_mail('Message from contact form', body, None, ['keugenemail@gmail.com'], fail_silently=False)
