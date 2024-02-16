from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView, PasswordResetView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView, LoginView, LogoutView
from django.urls import path

from .views import *

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # path('password_change/', CustomPasswordChangeView.as_view(), name="password-change"),
    # path('password_change/done/', PasswordChangeDoneView.as_view(), name="password-change-done"),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name="password-reset-done"),
    path('password_reset/', CustomPasswordResetView.as_view(), name="password-reset"),


    # path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    # path('reset/done/', PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]