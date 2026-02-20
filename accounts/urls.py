from django.contrib.auth.views import PasswordResetView
from django.urls import path

from accounts.views import *

urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('verify/',VerifyCodeView.as_view(),name='verify_register'),
    path('login/',LoginView.as_view(),name='login'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('password/forgot/',ForgetPasswordView.as_view(),name='forget_password'),
    path('password/verify/',VerifyForgetPasswordView.as_view(),name='verify_forget_password'),
    path('password/reset/',ChangePasswordView.as_view(),name='password_change'),
    path('vendor/request/',VendorRequestView.as_view(),name='request_vendor'),
    path('vendor/active/',ActiveVendorView.as_view(),name='active_vendor'),
    path('vendor/unactive/',UnactiveVendorView.as_view(),name='unactive_vendor'),
    path('vendor/<int:pk>/',AdminVendorApproveView.as_view(),name='admin_vendor_approve'),
    path('profile/',ProfileView.as_view(),name='profile'),
]