from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import *

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name="password-reset-done"),
    path('password_reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path('password_reset/complete/', CustomPasswordResetCompleteView.as_view(), name="password-reset-complete"),
    path('password_reset/', CustomPasswordResetView.as_view(), name="password-reset"),
]
