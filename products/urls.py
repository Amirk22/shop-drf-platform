from django.urls import path
from .views import *

urlpatterns = [
    path('',ProductView.as_view(),name='products'),
    path('<int:pk>/',ProductDetailView.as_view(),name='product_detail'),
    path('create/',CreateProductView.as_view(),name='product_create'),
    path('category/',CategoryView.as_view(),name='categories'),
    path('category/<int:pk>/',CategoryDetailView.as_view(),name='category_detail'),
    path('category/create/',CreateCategoryView.as_view(),name='category_create'),
    path('brand/',BrandView.as_view(),name='brands'),
    path('brand/<int:pk>/',BrandDetailView.as_view(),name='brand_detail'),
    path('brand/create/',CreateBrandView.as_view(),name='create_brand'),
    path('color/',ColorView.as_view(),name='colors'),
    path('color/create/',CreateColorView.as_view(),name='color_create'),
    path('color/<int:pk>/',ColorDetailView.as_view(),name='color_detail'),
]