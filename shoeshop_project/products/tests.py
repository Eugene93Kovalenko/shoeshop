from django.test import TestCase


a = {
  "after_expiration": 'null',
  "allow_promotion_codes": 'null',
  "amount_subtotal": 25000,
  "amount_total": 25000,
  "automatic_tax": {
    "enabled": 'false',
    "status": 'null'
  },
  "billing_address_collection": 'null',
  "cancel_url": "http://127.0.0.1:8000/cancel/",
  "client_reference_id": 'null',
  "consent": 'null',
  "consent_collection": 'null',
  "created": 1696868922,
  "currency": "usd",
  "currency_conversion": 'null',
  "custom_fields": [],
  "custom_text": {
    "shipping_address": 'null',
    "submit": 'null',
    "terms_of_service_acceptance": 'null'
  },
  "customer": 'null',
  "customer_creation": "if_required",
  "customer_details": {
    "address": {
      "city": 'null',
      "country": "RU",
      "line1": 'null',
      "line2": 'null',
      "postal_code": 'null',
      "state": 'null'
    },
    "email": "ad@yandex.ru",
    "name": "Eugene Kovalenko",
    "phone": 'null',
    "tax_exempt": "none",
    "tax_ids": []
  },
  "customer_email": "ad@yandex.ru",
  "expires_at": 1696955322,
  "id": "cs_test_a1oKXI4bfF2fBnIilVjaC4EaZ3NYeYvPtkvPncWjVsh1fO3KNtXN6azemW",
  "invoice": 'null',
  "invoice_creation": {
    "enabled": 'false',
    "invoice_data": {
      "account_tax_ids": 'null',
      "custom_fields": 'null',
      "description": 'null',
      "footer": 'null',
      "metadata": {},
      "rendering_options": 'null'
    }
  },
  "livemode": 'false',
  "locale": 'null',
  "metadata": {},
  "mode": "payment",
  "object": "checkout.session",
  "payment_intent": "pi_3NzMKAEHgFzglP9y0ShPy3GM",
  "payment_link": 'null',
  "payment_method_collection": "if_required",
  "payment_method_configuration_details": 'null',
  "payment_method_options": {},
  "payment_method_types": [
    "card"
  ],
  "payment_status": "paid",
  "phone_number_collection": {
    "enabled": 'false'
  },
  "recovered_from": 'null',
  "setup_intent": 'null',
  "shipping_address_collection": 'null',
  "shipping_cost": 'null',
  "shipping_details": 'null',
  "shipping_options": [],
  "status": "complete",
  "submit_type": 'null',
  "subscription": 'null',
  "success_url": "http://127.0.0.1:8000/success/",
  "total_details": {
    "amount_discount": 0,
    "amount_shipping": 0,
    "amount_tax": 0
  },
  "url": 'null'
}

print(a['id'])


