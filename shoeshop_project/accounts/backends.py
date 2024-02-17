from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


# class EmailAuthBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         user = get_user_model()
#         try:
#             user = user.objects.get(email=username)
#         except user.DoesNotExist:
#             return None
#         else:
#             if user.check_password(password):
#                 return user
#
#     def get_user(self, user_id):
#         user = get_user_model()
#         try:
#             return user.objects.get(pk=user_id)
#         except user.DoesNotExist:
#             return None
