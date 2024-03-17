from decimal import Decimal


Product.objects.create(
    name='SHOE',
    price=Decimal(100),
    discount=10,
    color='black',
    gende='Women',
    brand='Timberland',
    description='alfalkdjfksdjflksjdlfkjsd'
)

from django.db import connection


def run_custom_query():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM products_product")
        row = cursor.fetchone()
        print(row)


run_custom_query()
