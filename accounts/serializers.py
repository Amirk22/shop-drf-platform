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



