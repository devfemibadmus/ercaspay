from django.urls import path
from . import django
from .django import ERCASPAY_SETTINGS

urlpatterns = [
    path('', django.payment_page, name='ercaspay_payment_page'),
    path('admin', django.redirect_admin, name='ercaspay_admin_site'),
    path(ERCASPAY_SETTINGS['AUTH_REDIRECT_URL'], django.auth_page, name='ercaspay_auth_page'),
]
