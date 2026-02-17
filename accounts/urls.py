from django.urls import path

from accounts.views import *

urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('verify/',VerifyCodeView.as_view(),name='verify_register'),
    path('login/',LoginView.as_view(),name='login'),
    path('logout/',LogoutView.as_view(),name='logout'),
]