import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from config import settings

from django_tools.middlewares import ThreadLocal
from django.contrib.sessions.models import Session


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(blank=True, upload_to="category/%Y/%m/%d/")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product_app:category", kwargs={"category_name": self.name.lower()})

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Gender(models.Model):
    name = models.CharField(max_length=30, unique=True)
    image = models.ImageField(blank=True, upload_to="gender/%Y/%m/%d/")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Gender"
        verbose_name_plural = "Genders"


class Brand(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Brand"
        verbose_name_plural = "Brands"


class Color(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Color"
        verbose_name_plural = "Colors"


class Size(models.Model):
    name = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "Size"
        verbose_name_plural = "Sizes"
        ordering = ["name"]


class Product(models.Model):
    ORDERING_OPTIONS = [
        ('Popularity', '-popularity'),
        ('New', '-last'),
        ('Price high first', '-price'),
        ('Price low first', 'price')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    discount = models.PositiveIntegerField(
        default=0, blank=True, validators=[MinValueValidator(0), MaxValueValidator(99)]
    )
    # automatically updated via signals
    actual_price = models.DecimalField(max_digits=7, decimal_places=2, blank=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    description = models.TextField(blank=False)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    purchases_count = models.PositiveIntegerField(default=0)
    last_visit = models.DateTimeField(auto_now=True, blank=True, null=True)
    category = models.ManyToManyField(Category, related_name="products", blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("products:product-detail", kwargs={"pk": str(self.pk)})

    def get_add_to_cart_url(self):
        return reverse("orders:add-to-cart", kwargs={"pk": str(self.pk)})

    def get_remove_from_cart_url(self):
        return reverse("orders:remove-from-cart", kwargs={"pk": str(self.pk)})

    def get_gender_url(self):
        return reverse("products:gender", kwargs={"gender_slug": self.gender.name})

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "products"
        ordering = ["name"]


class ProductVariation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_variation', to_field='id')
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = ('product', 'size')
        verbose_name = "Product | Size"
        verbose_name_plural = "Product | Size"

    def __str__(self):
        return f"{self.product} / {self.size} size"


class ProductImage(models.Model):
    image = models.ImageField(upload_to="product/%Y/%m/%d/")
    is_main = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images", to_field='id')

    class Meta:
        verbose_name = "Photo"
        verbose_name_plural = "Photos"
        # ordering = ['product__-last_visit']

    def __str__(self):
        return self.image.name

    def get_absolute_url(self):
        return self.image.url


class Review(models.Model):
    RATING_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', to_field='id')
    rate = models.PositiveIntegerField(
        choices=RATING_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    text = models.TextField(max_length=3000, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']

    def __str__(self):
        return f'{str(self.user)} | {self.product} | {self.rate}'
