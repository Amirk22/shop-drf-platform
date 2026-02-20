from rest_framework import serializers
from .models import *

class ProductSerializer(serializers.ModelSerializer):
    vendor = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('id','created_at','updated_at')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('id',)



class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'
        read_only_fields = ('id',)


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'
        read_only_fields = ('id',)


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = '__all__'
        read_only_fields = ('id',)