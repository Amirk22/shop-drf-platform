from django.urls import path
from .views import *

urlpatterns = [
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("<int:order_id>/success/", PaymentSuccessView.as_view(), name="payment-success"),
    path("<int:order_id>/fail/", PaymentFailView.as_view(), name="payment-fail"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("<int:pk>/", PaymentDetailView.as_view(), name="payment-detail"),
    path('',PaymentView.as_view(),name='payment'),
]