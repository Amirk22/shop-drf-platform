from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import *
from .filters import ProductFilter
from accounts.models import VendorProfile
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from accounts.views import IsVendor , IsVendorOrAdmin
from rest_framework import filters
# Create your views here.


# Pagination

class ProductPagination(PageNumberPagination):
    page_size = 24
class GeneralPagination(PageNumberPagination):
    page_size = 12

# Product

class ProductView(generics.ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'description']

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related(
            'vendor','category','brand','color'
        ).prefetch_related('sizes')

class CreateProductView(generics.CreateAPIView):
    permission_classes = [IsVendor]
    serializer_class = ProductSerializer

    def perform_create(self,serializer):
        vendor = VendorProfile.objects.get(
            user=self.request.user,
            is_approved=True
        )
        serializer.save(vendor=vendor)

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsVendorOrAdmin]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Product.objects.all()

        return Product.objects.filter(
            vendor__user=self.request.user
        )

# Category

class CategoryView(generics.ListAPIView):
    serializer_class = CategorySerializer
    pagination_class = GeneralPagination
    def get_queryset(self):
        return Category.objects.all()

class CreateCategoryView(generics.CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = CategorySerializer

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

# Brand

class BrandView(generics.ListAPIView):
    serializer_class = BrandSerializer
    pagination_class = GeneralPagination
    queryset =  Brand.objects.all()

class CreateBrandView(generics.CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = BrandSerializer

class BrandDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = BrandSerializer
    queryset = Brand.objects.all()

# color

class ColorView(generics.ListAPIView):
    serializer_class = ColorSerializer
    pagination_class = GeneralPagination
    queryset = Color.objects.all()

class CreateColorView(generics.CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ColorSerializer

class ColorDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ColorSerializer
    queryset = Color.objects.all()

# Size

class SizeView(generics.ListAPIView):
    serializer_class = SizeSerializer
    pagination_class = GeneralPagination
    queryset = Size.objects.all()

class CreateSizeView(generics.CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = SizeSerializer
    queryset = Size.objects.all()

class SizeDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = SizeSerializer
    queryset = Size.objects.all()