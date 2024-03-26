import random
from random import randint

import factory
from factory import fuzzy

from faker import Faker

from accounts.models import CustomUser
from products.models import Product, Color, Gender, Brand, ProductVariation, Size, Review

fake = Faker()


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    price = fuzzy.FuzzyDecimal(100, 500)
    discount = fuzzy.FuzzyInteger(0, 20, step=5)
    description = fake.paragraph(nb_sentences=3)

    @factory.lazy_attribute
    def name(self) -> str:
        return f"{fake.word().capitalize()} {fake.word()} shoes"

    @factory.lazy_attribute
    def color(self) -> Color:
        return Color.objects.get(id=randint(1, 6))

    @factory.lazy_attribute
    def gender(self) -> Gender:
        return Gender.objects.get(id=randint(1, 2))

    @factory.lazy_attribute
    def brand(self) -> Brand:
        return Brand.objects.get(id=randint(1, 7))


class ProductVariationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductVariation

    @factory.lazy_attribute
    def size(self) -> Size:
        product = self.product
        size_objects = list(Size.objects.all())
        product_variations = ProductVariation.objects.filter(product=product)
        for product_var in product_variations:
            size_objects.remove(product_var.size)
        if size_objects:
            return size_objects[randint(0, len(size_objects) - 1)]
        else:
            return Size.objects.first()

    product = factory.SubFactory(ProductFactory)
    quantity = fuzzy.FuzzyInteger(10, 20, step=5)


class ProductReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review

    product = factory.SubFactory(ProductFactory)
    rate = fuzzy.FuzzyInteger(1, 5)
    text = fake.paragraph(nb_sentences=3)
    user = CustomUser.objects.all()[0]

    @factory.lazy_attribute
    def first_name(self) -> str:
        return fake.first_name()

    @factory.lazy_attribute
    def last_name(self) -> str:
        return fake.last_name()
