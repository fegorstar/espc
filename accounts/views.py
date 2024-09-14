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
from accounts.exceptions import CustomException
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
from accounts.permissions import IsUser, IsAdmin

#################### ALL STATIC PAGES #####################
# Register


def signup(request):
    return render(request, 'pages/register.html')

# Login


def signin(request):
    return render(request, 'pages/login.html')

# Dashboard


def dashboard(request):
    return render(request, 'pages/dashboard.html')


class CustomRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = [config('APP_SCHEME'), 'http', 'https']


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

        # Convert email to lowercase
        email = serializer.validated_data['email'].lower()

        try:
            # Save the validated data to the database
            with transaction.atomic():
                user = serializer.save(email=email)  # Save the lowercase email

                # Prepare response data
                response_data = {
                    'status': status.HTTP_201_CREATED,
                    'message': 'User registered successfully.',
                    'data': {
                        'full_name': f'{user.first_name} {user.last_name}',
                        'email': email,
                    }
                }

                # Return success response
                return Response(response_data, status=status.HTTP_201_CREATED)

        except IntegrityError:
            # If a user with the same email already exists, return a meaningful error response
            error_message = "A user with this email address already exists."
            return Response({'status_code': status.HTTP_400_BAD_REQUEST, 'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
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
        email = request.data.get('email').lower()  # Convert email to lowercase
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)

            if password and check_password(password, user.password):
                if not user.is_active:
                    raise CustomException(detail=_(
                        'Account disabled, contact admin!'), status_code=status.HTTP_401_UNAUTHORIZED)

                # Update user's last login
                update_last_login(None, user)

                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                # Fetch user profile
                profile = Profile.objects.get(user=user)
                profile_serializer = ProfileSerializer(profile)

                response_data = {
                    'status_code': status.HTTP_200_OK,
                    'message': _('User logged in successfully'),
                    'data': {
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email,
                        'user_type': user.user_type,  # Include user type
                        # Include profile image
                        'profile_picture': profile_serializer.data.get("profile_picture"),
                        'state': profile_serializer.data.get("state"),
                        'city': profile_serializer.data.get("city"),
                        'tokens': {
                            'refresh': refresh_token,
                            'access': access_token,
                        },
                    }
                }
                return Response(response_data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            pass

        raise CustomException(detail=_(
            'Invalid login credentials!'), status_code=status.HTTP_401_UNAUTHORIZED)
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

        # Add a custom message to the response
        response_data = {'error': 'Successfully logged out.'}
        return Response(response_data, status=status.HTTP_200_OK)
##########################################################################################
