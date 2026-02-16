from django.urls import path

from accounts.views import *

urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('verify/',VerifyCodeView.as_view(),name='verify_register'),
]