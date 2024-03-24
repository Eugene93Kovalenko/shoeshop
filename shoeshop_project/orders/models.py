from django_countries.fields import CountryField

from products.models import *


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    product_variation = models.ForeignKey(ProductVariation, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} pcs | {self.product_variation.product.name} | {self.product_variation.size} size |" \
               f" {self.user} | Ordered: {self.ordered}"

    class Meta:
        verbose_name = "Product in cart"
        verbose_name_plural = "Products in cart"

    def get_remove_from_cart_url(self):
        return reverse("orders:remove-from-cart", kwargs={"slug": self.product_variation.product.slug})


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    products = models.ManyToManyField(OrderItem, related_name='shipping_address')
    delivery_price = models.DecimalField(default=50, max_digits=7, decimal_places=2)
    start_datetime = models.DateTimeField(auto_now_add=True)
    ordered_datetime = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'ShippingAddress',
        related_name='shipping_address',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    def __str__(self):
        if self.ordered:
            return f"{self.user} | Ordered: {self.ordered} | {self.ordered_datetime}"
        return f"{self.user} | Ordered: {self.ordered}"

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"


class ShippingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    country = CountryField(multiple=False)
    region = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    zip = models.CharField(max_length=20)
    address = models.CharField(max_length=150)
    default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f'{self.user} | {self.city} | {self.address}'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments', null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
