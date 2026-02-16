from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.cache import cache
from django.core.mail import send_mail
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from rest_framework.throttling import UserRateThrottle
from .serializers import *
import secrets
import string

# Create your views here.

def generate_6digit_code():
    return ''.join(secrets.choice(string.digits) for _ in range(6))
class RegisterThrottle(UserRateThrottle):
    rate = '5/hour'

class RegisterView(APIView):

    throttle_classes = [RegisterThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email'].lower()
            password = serializer.validated_data['password']

            if User.objects.filter(email__iexact=email).exists():
                return Response({"error": "Email already exists"}, status=409)

            password_hashed = make_password(password)
            cache.set(f"register_user_{email}", {'email': email, 'password': password_hashed}, timeout=300)
            code = str(generate_6digit_code())
            cache.set(f"register_code_{email}", code, timeout=300)


            send_mail(
                "Verify your email",
                f'your verify code is {code}',
                'marketplace@gmail.com',
                [email],
                fail_silently=False,
            )
            return Response({"message": "Send Verify Code"}, status=200)
        return Response(serializer.errors, status=400)

class VerifyCodeView(APIView):

    throttle_classes = [RegisterThrottle]

    def post(self, request):
        serializer = VerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email'].lower()
            code = serializer.validated_data['code'].strip()

            saved_code = cache.get(f"register_code_{email}")
            data = cache.get(f"register_user_{email}")
            attempt_key = f"verify_attempt_{email}"
            attempts = cache.get(attempt_key, 0)

            if attempts >= 5:
                return Response({"error": "Too many attempts"}, status=429)

            if not saved_code or not data:
                return Response({"error": "Code has expired."}, status=400)

            if saved_code != code:
                cache.set(attempt_key, attempts + 1, timeout=300)
                return Response({"error": "The code is wrong."}, status=400)

            User.objects.create(
                username=email,
                email=email,
                password=data['password']
            )

            cache.delete(f"register_user_{email}")
            cache.delete(f"register_code_{email}")
            cache.delete(attempt_key)

            return Response({"message": "Register is successful."}, status=201)
        return Response(serializer.errors, status=400)
