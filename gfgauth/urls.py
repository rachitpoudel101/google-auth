from django.urls import path
from . import views

urlpatterns = [
    path('gmailAuthenticate', views.gmail_authenticate, name='gmail_authenticate'),
    path('oauth2callback', views.auth_return, name='oauth2callback'),
    path('', views.home, name='home'),
]
