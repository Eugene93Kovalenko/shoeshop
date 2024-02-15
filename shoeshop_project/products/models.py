from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import SearchVectorField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from config import settings


class Category(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(blank=True, upload_to="category/%Y/%m/%d/")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product_app:category", kwargs={"category_name": self.name.lower()})

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Gender(models.Model):
    name = models.CharField(max_length=30)
    image = models.ImageField(blank=True, upload_to="gender/%Y/%m/%d/")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Gender"
        verbose_name_plural = "Genders"


class Brand(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Brand"
        verbose_name_plural = "Brands"


class Color(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Color"
        verbose_name_plural = "Colors"


class Size(models.Model):
    name = models.PositiveIntegerField()

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "Size"
        verbose_name_plural = "Sizes"


class Product(models.Model):
    ORDERING_OPTIONS = [
        ('Popularity', '-num_visits'),
        ('Last', '-created_at'),
        ('Price high first', '-price'),
        ('Price low first', 'price')
    ]

    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    discount_price = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
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

    # def counter(self):
    #     return self.num_visits += 1

    def get_absolute_url(self):
        return reverse("products:product-detail", kwargs={"product_slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse("orders:add-to-cart", kwargs={"slug": self.slug})

    def get_remove_from_cart_url(self):
        return reverse("orders:remove-from-cart", kwargs={"slug": self.slug})

    def get_gender_url(self):
        return reverse("products:gender", kwargs={"gender_slug": self.gender.name})

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "products"
        ordering = ["name"]


class ProductVariation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_variation')
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
    is_active = models.BooleanField(default=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")

    class Meta:
        verbose_name = "Photo"
        verbose_name_plural = "Photos"

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
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rate = models.PositiveIntegerField(choices=RATING_CHOICES,
                                       validators=[MinValueValidator(1), MaxValueValidator(5)])
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
