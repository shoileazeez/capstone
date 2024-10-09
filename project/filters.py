import django_filters
from .models import Product
from django_filters import rest_framework as filters

class ProductFilter(django_filters.FilterSet):
    category = django_filters.ChoiceFilter(field_name='category__category', choices=[
        ('cloth', 'Cloth'),
        ('electronics', 'Electronics'),
        ('shoes', 'Shoes'),
    ])
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte') 
    in_stock = django_filters.BooleanFilter(field_name='stock_quantity', method='filter_in_stock')

    class Meta:
        model = Product
        fields = ['category', 'min_price', 'max_price', 'in_stock']

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock_quantity__gt=0)  # Only include products that are in stock
        return queryset  # If the filter is not applied, return all products

from datetime import date

class DateFilter(filters.FilterSet):
    year = django_filters.NumberFilter(field_name='created_at', lookup_expr='year')
    month = django_filters.NumberFilter(field_name='created_at', lookup_expr='month')
    day = django_filters.NumberFilter(field_name='created_at', lookup_expr='day')

    class Meta:
        model = Product
        fields = ['category']

    # def filter_queryset(self, queryset):
    #     today = date.today()

    #     # Prevent filtering for future years
    #     if self.data.get('year') and int(self.data['year']) > today.year:
    #         raise ValueError("The year cannot be in the future.")

    #     return super().filter_queryset(queryset)



