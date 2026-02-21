from django.urls import path

from orders.views import *

urlpatterns = [
    path('', CartDetailView.as_view(),name='cart_detail'),
    path('add/', AddToCartView.as_view(),name='add_to_cart'),
    path('remove/',RemoveFromCartView.as_view(),name='remove_from_cart'),
]