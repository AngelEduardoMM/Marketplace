from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm

class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('usuarios:login')  # Redirige al login tras logout

class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')  # Redirige al login tras registrarse
# Create your views here.