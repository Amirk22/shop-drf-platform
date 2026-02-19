from rest_framework import serializers
from accounts.models import *


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(write_only=True,min_length=8)
    confirm_password = serializers.CharField(write_only=True,min_length=8)
    def validate_email(self,value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    def validate(self,data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return data

class VerifySerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    code = serializers.CharField(max_length=6, min_length=6)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(write_only=True,min_length=8)


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)

class VerifyForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    code = serializers.CharField(max_length=6, min_length=6)

class ChangePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    reset_token = serializers.CharField()
    password = serializers.CharField(write_only=True,min_length=8)
    confirm_password = serializers.CharField(write_only=True,min_length=8)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return data


class VendorRequestSerializer(serializers.Serializer):
    shop_name = serializers.CharField(max_length=255)

class ActiveVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = "__all__"

class VendorApproveSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = "__all__"
        read_only_fields = ["id","shop_name","user"]

class VendorProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    class Meta:
        model = VendorProfile
        fields = ["id", "shop_name", "is_approved", "email"]

class CustomerProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    class Meta:
        model = CustomerProfile
        fields = ["id", "email"]

class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email"]