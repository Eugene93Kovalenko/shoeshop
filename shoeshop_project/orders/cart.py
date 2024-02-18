from decimal import Decimal

from config import settings
from products.models import ProductVariation


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.setdefault(settings.CART_SESSION_ID, {})
        self.cart = cart

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def __iter__(self):
        product_variation_ids = self.cart.keys()
        product_variations = ProductVariation.objects.filter(id__in=product_variation_ids)
        cart = self.cart

        for product_variation in product_variations:
            cart[str(product_variation.id)]['product_variation'] = product_variation

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total'] = item['price'] * item['quantity']
            yield item

    def add(self, product_variation, quantity, user):
        product_variation_id = str(product_variation.id)
        if product_variation_id not in self.cart:
            self.cart[product_variation_id] = {'quantity': quantity,
                                               'price': str(product_variation.product.get_actual_price),
                                               'user': user}
        else:
            self.cart[product_variation_id]['quantity'] += quantity
        self.save()

    def delete(self, product_variation):
        product_id = str(product_variation.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def save(self):
        self.session.modified = True

    def get_total_all_products_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def get_delivery_price(self):
        if self.get_total_all_products_price():
            return Decimal('50.00')
        return 0

    def get_final_order_price(self):
        return self.get_total_all_products_price() + self.get_delivery_price()



