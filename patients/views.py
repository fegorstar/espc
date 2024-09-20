import cloudinary.uploader
from django.utils import timezone
from rest_framework import serializers
from django.db import IntegrityError, transaction
from rest_framework.exceptions import NotFound, ValidationError
from django.db.models import Sum, F, ExpressionWrapper, DurationField, Prefetch
from django.conf import settings
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ProfileUpdateSerializer, ProfileSerializer, EmailChangeSerializer, PasswordChangeSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from utils.permissions_utils import IsUser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from accounts.models import User
from .models import Profile
from utils.response_utils import success_response, error_response
from administrator.models import PatientReport
from django.shortcuts import get_object_or_404
########################## User Profile Management ##############################################

############################# ProfileUpdateAPIView ##########################################

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
            if not request.user.is_authenticated:
                return error_response("Authentication credentials were not provided.", status_code=status.HTTP_401_UNAUTHORIZED)

            profile = get_object_or_404(Profile, user=request.user)
            data = request.data.copy()
            serializer = self.serializer_class(profile, data=data, context={'request': request})

            if serializer.is_valid():
                instance = serializer.save()
                serialized_data = self.serializer_class(instance).data
                return success_response("Profile updated successfully", data=serialized_data)

            return error_response("Invalid data", validation_errors=serializer.errors)

        except Exception as e:
            return error_response(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            profile = get_object_or_404(Profile, user=request.user)
            serializer = ProfileSerializer(profile)
            return success_response("Profile details retrieved successfully", data=serializer.data)

        except Exception as e:
            return error_response(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

################################################################################################

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
        user = request.user
        user_id = kwargs.get('user_id')
        
        if str(user_id) != str(user.id):
            return error_response("You do not have permission to deactivate this account.", status_code=status.HTTP_403_FORBIDDEN)

        user.is_active = False
        user.save()
        return success_response("User deactivated successfully")

################################################################################################

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
            return success_response("Email changed successfully")
        return error_response("Invalid data", validation_errors=serializer.errors)

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
                return error_response("Old password is not correct", validation_errors={"old_password": ["Old password is not correct"]})
            user.set_password(new_password)
            user.save()
            return success_response("Password changed successfully")
        return error_response("Invalid data", validation_errors=serializer.errors)

################################################################################################

############################## ReportHistoryAPIView ###########################################################
class ReportHistoryAPIView(APIView):
    permission_classes = [IsUser]

    @swagger_auto_schema(
        tags=["Patient Diagnosis Management"],
        operation_summary="Get Recent User Report History",
        operation_description="Retrieve the most recent report analyses of the user.",
        responses={
            200: openapi.Response(
                description="Recent report history retrieved successfully.",
                schema=openapi.Schema(
                    type="object",
                    properties={
                        "status_code": openapi.Schema(type="integer", example=200),
                        "message": openapi.Schema(type="string", example="Recent report history retrieved successfully."),
                        "data": openapi.Schema(
                            type="array",
                            items=openapi.Schema(
                                type="object",
                                properties={
                                    "id": openapi.Schema(type="integer", example=1),
                                    "created_at": openapi.Schema(type="string", format="date-time"),
                                    "diagnosis": openapi.Schema(type="string", example="Flu"),
                                    "age": openapi.Schema(type="integer", example=30),
                                    "sex": openapi.Schema(type="string", example="Male"),
                                }
                            )
                        )
                    }
                )
            ),
            404: openapi.Response(description="No report history found"),
            401: openapi.Response(description="Unauthorized"),
        }
    )
    def get(self, request, *args, **kwargs):
        reports = PatientReport.objects.filter(patient=request.user).order_by('-created_at')[:5]

        if not reports.exists():
            return error_response("No report history found", status_code=status.HTTP_404_NOT_FOUND)

        report_data = [
            {
                "id": report.id,
                "created_at": report.created_at,
                "diagnosis": report.diagnosis.name if report.diagnosis else "Not diagnosed",
                "age": report.age,
                "sex": report.sex,
            }
            for report in reports
        ]

        return success_response("Recent report history retrieved successfully.", data=report_data)

###################################################################################################################################