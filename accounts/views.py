from rest_framework import generics
from rest_framework.response import Response
from django.core.cache import cache
from django.core.mail import send_mail
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from rest_framework.throttling import UserRateThrottle
from .serializers import *
import secrets
import string
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import AnonRateThrottle
from rest_framework.permissions import IsAdminUser, IsAuthenticated, BasePermission
from rest_framework import permissions

# Create your views here.


class IsVendor(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        vendor = VendorProfile.objects.filter(user=user).first()
        if not vendor:
            return False

        return vendor.is_approved


class IsVendorOrAdmin(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        return VendorProfile.objects.filter(
            user=request.user,
            is_approved=True
        ).exists()


class ProductDetailPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_superuser or obj.vendor.user == request.user


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

            user = User.objects.create(
                username=email,
                email=email,
                password=data['password']
            )
            CustomerProfile.objects.create(
                user=user
            )

            cache.delete(f"register_user_{email}")
            cache.delete(f"register_code_{email}")
            cache.delete(attempt_key)

            return Response({"message": "Register is successful."}, status=201)
        return Response(serializer.errors, status=400)


class LoginThrottle(AnonRateThrottle):
    rate = '10/hour'
class LoginView(APIView):

    throttle_classes = [LoginThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email'].strip().lower()
            password = serializer.validated_data['password']

            user = User.objects.filter(email__iexact=email).first()
            if not user or not user.check_password(password):
                return Response({'error': 'Incorrect email or password.'}, status=400)

            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=200)

        return Response(serializer.errors, status=400)


class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required."},
                status=400
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=200)
        except Exception:
            return Response(
                {"error": "Invalid or expired token."},
                status=400
            )


class ForgetPasswordThrottle(AnonRateThrottle):
    rate = '5/hour'
class ForgetPasswordView(APIView):

    throttle_classes = [ForgetPasswordThrottle]

    def post(self, request):
        serializer = ForgetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email'].lower()

            if not User.objects.filter(email__iexact=email).exists():
                return Response(
                    {"message": "If the email exists, a verification code has been sent."},
                    status=200
                )

            code = str(generate_6digit_code())
            cache.set(f"forget_password_code_{email}", code, timeout=300)

            send_mail(
                "Verify your email",
                f'your verify code is {code}',
                'marketplace@gmail.com',
                [email],
                fail_silently=False,
            )
            return Response({"message": "Send Verify Code"}, status=200)
        return Response(serializer.errors, status=400)

class VerifyForgetPasswordView(APIView):

    throttle_classes = [ForgetPasswordThrottle]

    def post(self, request):
        serializer = VerifyForgetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email'].lower()
            code = serializer.validated_data['code'].strip()

            saved_code = cache.get(f"forget_password_code_{email}")
            attempt_key = f"verify_attempt_{email}"
            attempts = cache.get(attempt_key, 0)

            if attempts >= 5:
                return Response({"error": "Too many attempts"}, status=429)

            if saved_code and saved_code == code:
                reset_token = secrets.token_urlsafe(32)
                cache.set(f"reset_token_{email}", reset_token, timeout=300)
                cache.delete(attempt_key)
                cache.delete(f"forget_password_code_{email}")
                return Response({
                    "message": "Code verified.",
                    "reset_token": reset_token
                })

            cache.set(attempt_key, attempts + 1, timeout=300)
            return Response({"error": "Incorrect code."}, status=400)

class ChangePasswordView(APIView):

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email'].lower()
            new_password = serializer.validated_data['password']
            reset_token = serializer.validated_data['reset_token']

            saved_token = cache.get(f"reset_token_{email}")

            if not saved_token or saved_token != reset_token:
                return Response({"error": "Invalid or expired token."}, status=403)

            user = User.objects.filter(email__iexact=email).first()
            if not user:
                return Response({"error": "Invalid request."}, status=400)

            user.set_password(new_password)
            user.save()

            cache.delete(f"reset_token_{email}")

            return Response({"message": "Password changed."}, status=200)

        return Response(serializer.errors, status=400)


class VendorRequestView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if hasattr(request.user, 'vendor_profile'):
            return Response({"error": "Already requested."}, status=400)

        serializer = VendorRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        VendorProfile.objects.create(
            user=request.user,
            shop_name=serializer.validated_data['shop_name'].title()
        )

        return Response({"message": "Request sent."}, status=201)

class ActiveVendorView(generics.ListAPIView):

    queryset = VendorProfile.objects.filter(is_approved=True)
    serializer_class = ActiveVendorSerializer
    permission_classes = [IsAdminUser]

class UnactiveVendorView(generics.ListAPIView):

    queryset = VendorProfile.objects.filter(is_approved=False)
    serializer_class = ActiveVendorSerializer
    permission_classes = [IsAdminUser]

class AdminVendorApproveView(generics.UpdateAPIView):
    serializer_class = VendorApproveSerializer
    queryset = VendorProfile.objects.all()
    permission_classes = [IsAdminUser]

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.is_superuser:
            return Response(AdminProfileSerializer(user).data)

        vendor = VendorProfile.objects.filter(user=user).first()
        if vendor:
            return Response(VendorProfileSerializer(vendor).data)

        customer = CustomerProfile.objects.filter(user=user).first()
        if customer:
            return Response(CustomerProfileSerializer(customer).data)

        return Response({"detail": "Profile not found"}, status=404)