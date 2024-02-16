import factory
from faker import Faker

from accounts.models import CustomUser


fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser

    # username = factory.Faker('username')
    username = fake.name()
    is_stuff = 'True'
