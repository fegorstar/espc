from django.db import transaction
from django.db import IntegrityError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from drf_yasg import openapi
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from rest_framework import permissions
from rest_framework_simplejwt.tokens import TokenError
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.contrib.sites.shortcuts import get_current_site
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import RegisterSerializer, LoginSerializer, VerificationRequestSerializer, LogoutSerializer, ResendVerificationCodeSerializer, ResetPasswordEmailRequestSerializer, SetNewPasswordSerializer
from .utils import Util, generate_verification_code
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework import generics, status, views, permissions
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from decouple import config, Csv
from django.http import HttpResponsePermanentRedirect
from django.contrib.auth.models import update_last_login
from rest_framework import generics
from patients.models import Profile
from accounts.models import User
from patients.serializers import ProfileSerializer
from django.shortcuts import get_object_or_404, redirect, render
from utils.permissions_utils import IsUser, IsAdmin
from utils.response_utils import success_response, error_response
#################### ALL STATIC PAGES #####################
def signup(request):
    return render(request, 'pages/register.html')

# Login
def signin(request):
    return render(request, 'pages/login.html')

# Dashboard
def dashboard(request):
    return render(request, 'pages/dashboard.html')


# Search History
def search_history(request):
    return render(request, 'pages/search_history.html')

# Profile
def profile(request):
    return render(request, 'pages/profile.html')

###############################  RegisterView #########################################
class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_summary="User Registration",
        operation_description="Register a new user.",
        responses={
            201: "User registered successfully.",
            400: "Bad request. Check the request payload.",
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email'].lower()

        try:
            with transaction.atomic():
                user = serializer.save(email=email)

                return success_response(
                    message='User registered successfully.',
                    data={
                        'full_name': f'{user.first_name} {user.last_name}',
                        'email': email,
                    },
                    status_code=status.HTTP_201_CREATED
                )

        except IntegrityError:
            return error_response(
                message="A user with this email address already exists.",
                status_code=status.HTTP_400_BAD_REQUEST
            )
#########################################################################################################################

################################## LoginAPIView #############################################
class LoginAPIView(APIView):
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_summary="User Login",
        operation_description="Login with email and password.",
        request_body=LoginSerializer,
        responses={
            200: "Login successful.",
            400: "Bad request. Check the request payload.",
            401: "Unauthorized. Invalid login credentials."
        }
    )
    def post(self, request):
        email = request.data.get('email').lower()
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)

            if password and check_password(password, user.password):
                if not user.is_active:
                    return error_response(
                        message='Account disabled, contact admin!',
                        status_code=status.HTTP_401_UNAUTHORIZED
                    )

                update_last_login(None, user)

                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                profile = Profile.objects.get(user=user)
                profile_serializer = ProfileSerializer(profile)

                return success_response(
                    message='User logged in successfully',
                    data={
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email,
                        'user_type': user.user_type,
                        'profile_picture': profile_serializer.data.get("profile_picture"),
                        'state': profile_serializer.data.get("state"),
                        'city': profile_serializer.data.get("city"),
                        'tokens': {
                            'refresh': refresh_token,
                            'access': access_token,
                        },
                    },
                    status_code=status.HTTP_200_OK
                )

        except User.DoesNotExist:
            pass

        return error_response(
            message='Invalid login credentials!',
            status_code=status.HTTP_401_UNAUTHORIZED
        )
###################################################################################################


############################# LogoutAPIView #######################################################
class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_summary="User Logout",
        operation_description="Logout the user and invalidate their tokens.",
        request_body=LogoutSerializer,
        responses={
            200: "Logout successful.",
            401: "Unauthorized. User not authenticated.",
        }
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return success_response(
            message='Successfully logged out.',
            status_code=status.HTTP_200_OK
        )
##########################################################################################
