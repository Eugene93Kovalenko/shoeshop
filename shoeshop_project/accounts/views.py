from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, RedirectURLMixin, \
    PasswordResetDoneView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, TemplateView

from accounts.forms import CustomAuthenticationForm, CustomUserCreationForm, CustomPasswordChangeForm, \
    CustomPasswordResetForm


class CustomLoginView(SuccessMessageMixin, LoginView):
    form_class = CustomAuthenticationForm
    success_message = 'You have successfully logged in!'

    def get_success_url(self):
        return self.request.POST['return_to']


class RegisterView(SuccessMessageMixin, FormView):
    form_class = CustomUserCreationForm
    template_name = 'registration/registration.html'
    success_message = 'You have successfully signed up!'

    #todo
    def get_success_url(self):
        if 'login' in self.request.POST['return_to']:
            return reverse_lazy("products:home")
        return self.request.POST['return_to']

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterView, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('products:home')
        return super(RegisterView, self).get(request, *args, **kwargs)


# class CustomPasswordChangeView(PasswordChangeView):
#     form_class = CustomPasswordChangeForm
#     success_url = reverse_lazy("accounts:password-change-done")
#     template_name = 'registration/password_change.html'


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy("accounts:password-reset-done")
    template_name = 'registration/password_reset.html'


class CustomPasswordResetDoneView(TemplateView):
    # form_class = CustomPasswordResetForm
    # success_url = reverse_lazy("accounts:password-reset-done")
    template_name = "registration/password_reset_confirmation.html"
