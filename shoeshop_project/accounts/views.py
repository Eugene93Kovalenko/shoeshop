from django.contrib.auth import login
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView
from django.http import HttpResponseRedirect, HttpResponse

from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from accounts.forms import CustomAuthenticationForm, CustomUserCreationForm, CustomPasswordResetForm


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    success_url = reverse_lazy("products:home")


class RegisterView(FormView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/registration.html'
    success_url = reverse_lazy("products:home")

    def form_valid(self, form) -> HttpResponseRedirect:
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterView, self).form_valid(form)

    def get(self, request, *args, **kwargs) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect('products:home')
        return super(RegisterView, self).get(request, *args, **kwargs)


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy("accounts:password-reset-done")


class CustomPasswordResetDoneView(TemplateView):
    template_name = "accounts/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password-reset-complete")


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"
