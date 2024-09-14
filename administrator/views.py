from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView
import joblib
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import DiagnosisSerializer, ADRReportSerializer
from .models import Diagnosis
from accounts.exceptions import CustomException
from accounts.permissions import IsUser


class ReportADRAPIView(APIView):
    permission_classes = [IsUser]

    @swagger_auto_schema(
        tags=["Patient ADR Management"],
        operation_summary="Report Adverse Drug Reaction",
        operation_description="Submit a report for an adverse drug reaction (ADR).",
        request_body=ADRReportSerializer,
        responses={
            201: openapi.Response(
                description="ADR report submitted successfully.",
                schema=openapi.Schema(
                    type="object",
                    properties={
                        "status_code": openapi.Schema(type="integer", example=201),
                        "message": openapi.Schema(type="string", example="ADR report submitted successfully."),
                        "data": openapi.Schema(
                            type="object",
                            properties={
                                "id": openapi.Schema(type="integer", example=1),
                                "patient": openapi.Schema(type="integer", example=1),
                                "drug": openapi.Schema(type="integer", example=1),
                                "symptoms": openapi.Schema(type="string", example="Nausea, headache"),
                                "created_at": openapi.Schema(type="string", format="date-time", example="2024-07-29T00:52:12.031752+01:00"),
                                "updated_at": openapi.Schema(type="string", format="date-time", example="2024-07-29T00:52:12.031752+01:00")
                            }
                        )
                    }
                )
            ),
            400: openapi.Response(description="Bad Request"),
            401: openapi.Response(description="Unauthorized")
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = ADRReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(patient=request.user)
            return Response({
                "status_code": status.HTTP_201_CREATED,
                "message": "ADR report submitted successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        raise CustomException(detail=serializer.errors,
                              status_code=status.HTTP_400_BAD_REQUEST)
