import django_filters
from .models import Product, Size

class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    sizes = django_filters.ModelMultipleChoiceFilter(
        field_name='sizes',
        queryset=Size.objects.all()
    )

    class Meta:
        model = Product
        fields = ['category', 'brand', 'color', 'sizes']