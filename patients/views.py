import cloudinary.uploader
from django.utils import timezone
from datetime import timedelta
from rest_framework import serializers
from django.db import IntegrityError, transaction
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import get_object_or_404
from django.db.models import Sum, F, ExpressionWrapper, DurationField, Prefetch
from django.conf import settings
from rest_framework import permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ProfileUpdateSerializer, ProfileSerializer, EmailChangeSerializer, PasswordChangeSerializer
from accounts.exceptions import CustomException
from rest_framework.parsers import MultiPartParser, FormParser
from accounts.permissions import IsUser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import validate_email
from django.template.loader import render_to_string
from accounts.models import User
from accounts.utils import Util
from django.utils.translation import gettext_lazy as _
from .models import Profile

########################## User Profile Management ##############################################

#############################  ProfileUpdateAPIView ##########################################


class ProfileUpdateAPIView(APIView):
    serializer_class = ProfileUpdateSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsUser]

    @swagger_auto_schema(
        tags=["User Profile Management"],
        operation_summary="Update Profile",
        operation_description="Update the profile details.",
        request_body=ProfileUpdateSerializer,
        responses={
            200: openapi.Response(description="Profile updated successfully"),
            400: "Bad Request",
            404: "Profile not found"
        }
    )
    def put(self, request, *args, **kwargs):
        try:
            # Check if user is authenticated
            if not request.user.is_authenticated:
                raise CustomException(
                    detail="Authentication credentials were not provided.", status_code=status.HTTP_401_UNAUTHORIZED)

            # Fetch the profile based on the authenticated user
            profile = Profile.objects.get(user=request.user)
            data = request.data.copy()  # Make a copy of request data

            serializer = self.serializer_class(
                profile, data=data, context={'request': request})

            if serializer.is_valid():
                # Save the updated profile
                instance = serializer.save()

                # Retrieve the serialized data with properly formatted subjects
                serialized_data = self.serializer_class(instance).data

                # Return the serialized data
                return Response({"status": status.HTTP_200_OK, "message": "Profile updated successfully", "data": serialized_data}, status=status.HTTP_200_OK)

            return Response({"status": status.HTTP_400_BAD_REQUEST, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Profile.DoesNotExist:
            raise CustomException(detail="Profile not found",
                                  status_code=status.HTTP_404_NOT_FOUND)

        except CustomException as e:
            return Response({"error": e.detail['error']}, status=e.status_code)
################################################################################################

###################### ProfileDetailAPIView ###############################################


class ProfileDetailAPIView(APIView):
    permission_classes = [IsUser]

    @swagger_auto_schema(
        tags=["User Profile Management"],
        operation_summary="Get Profile Details",
        operation_description="Get the profile details of the authenticated user.",
        responses={
            200: openapi.Response(description="Profile details retrieved successfully"),
            401: "Unauthorized"
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            profile = Profile.objects.get(user=user)
            serializer = ProfileSerializer(profile)

            # Create the response data
            response_data = {
                "status": status.HTTP_200_OK,
                "profile": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            raise CustomException(detail="Profile not found",
                                  status_code=status.HTTP_404_NOT_FOUND)

        except CustomException as e:
            return Response({"error": e.detail['error']}, status=e.status_code)
###############################################################################################################


####################### DeactivateAccountAPIView #########################################
class DeactivateAccountAPIView(APIView):
    permission_classes = [IsUser]

    @swagger_auto_schema(
        tags=["User Profile Management"],
        operation_summary="Deactivate User Account",
        operation_description="Deactivate the authenticated user's account.",
        responses={
            200: "User deactivated successfully.",
            403: "Forbidden. You do not have permission to deactivate this account."
        }
    )
    def patch(self, request, *args, **kwargs):
        # Get the authenticated user
        user = request.user

        # Check if the user ID in the URL matches the authenticated user's ID
        user_id = kwargs.get('user_id')
        if str(user_id) != str(user.id):
            return Response({'error': 'You do not have permission to deactivate this account.'}, status=status.HTTP_403_FORBIDDEN)

        # Deactivate the user's account
        user.is_active = False
        user.save()

        return Response({'success': True, 'message': 'User deactivated successfully'}, status=status.HTTP_200_OK)
############################################################################################################

##################### EmailChangeAPIView #########################################


class EmailChangeAPIView(APIView):
    serializer_class = EmailChangeSerializer
    permission_classes = [IsUser]

    @swagger_auto_schema(
        tags=["User Profile Management"],
        operation_summary="Change Email",
        operation_description="Change the email address of the user.",
        request_body=EmailChangeSerializer,
        responses={
            200: openapi.Response(description="Email changed successfully"),
            400: "Bad Request",
            404: "User not found"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = request.user
            new_email = serializer.validated_data['new_email']
            user.email = new_email
            user.save()
            return Response({"detail": "Email changed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
##################################################################################################################


############################### PasswordChangeAPIView ##############################

class PasswordChangeAPIView(APIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsUser]

    @swagger_auto_schema(
        tags=["User Profile Management"],
        operation_summary="Change Password",
        operation_description="Change the password of the user.",
        request_body=PasswordChangeSerializer,
        responses={
            200: openapi.Response(description="Password changed successfully"),
            400: "Bad Request",
            404: "User not found"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            if not user.check_password(old_password):
                return Response({"old_password": ["Old password is not correct"]}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_password)
            user.save()
            return Response({"detail": "Password changed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
######################################################################################################
