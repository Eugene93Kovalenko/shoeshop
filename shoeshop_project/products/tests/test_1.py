import pytest
from django.contrib.auth.models import User

from accounts.models import CustomUser


@pytest.mark.django_db
def test_new_user(user_factory):
    count = CustomUser.objects.all().count()
    print(count)
    assert count == 1
