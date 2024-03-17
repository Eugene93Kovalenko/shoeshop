from decimal import Decimal

from config import settings


class Cart:
    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.setdefault(settings.CART_SESSION_ID, {})

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def __iter__(self):
        for item in self.cart.values():
            yield item

    def add(self, product_variation, quantity, user=None):
        product_variation_id = str(product_variation.id)
        if product_variation_id not in self.cart:
            self.cart[product_variation_id] = {
                'quantity': quantity,
                'price': str(product_variation.product.actual_price),
                'user_id': user,
                'total': str(quantity * product_variation.product.actual_price),
                'product_name': product_variation.product.name,
                'product_id': str(product_variation.product.id),
                'product_url': product_variation.product.get_absolute_url(),
                'product_remove_url': product_variation.product.get_remove_from_cart_url(),
                'product_variation_id': product_variation.id,
                'size': product_variation.size.name,
                'image_url': product_variation.product.images.first().get_absolute_url(),
            }
        else:
            self.cart[product_variation_id]['quantity'] += quantity
        self.save()

    def update_price(self, instance):
        for item in self.cart.values():
            if item['product_name'] == instance.name:
                item['price'] = str(instance.price)
                item['total'] = item['price'] * item['quantity']
        self.save()

    def delete(self, product_variation):
        product_variation_id = str(product_variation.id)
        if product_variation_id in self.cart:
            del self.cart[product_variation_id]
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
