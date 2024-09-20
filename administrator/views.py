from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import DiagnosisSerializer, PatientReportSerializer, DrugSerializer, SymptomSerializer
from .models import Diagnosis, Drug, PatientReport, Symptom
from utils.permissions_utils import IsUser
from utils.response_utils import success_response, error_response




############################## ReportDiagnosisAPIView ###########################################################
class ReportDiagnosisAPIView(APIView):
    permission_classes = [IsUser]

    @swagger_auto_schema(
        tags=["Patient Diagnosis Management"],
        operation_summary="Report Symptoms and Generate Diagnosis",
        operation_description="Submit a report for symptoms to receive a diagnosis and drug recommendations.",
        request_body=PatientReportSerializer,
        responses={
            201: openapi.Response(
                description="Diagnosis generated successfully.",
                schema=openapi.Schema(
                    type="object",
                    properties={
                        "status_code": openapi.Schema(type="integer", example=201),
                        "message": openapi.Schema(type="string", example="Diagnosis generated successfully."),
                        "data": openapi.Schema(
                            type="object",
                            properties={
                                "patient_info": openapi.Schema(
                                    type="object",
                                    properties={
                                        "email": openapi.Schema(type="string", example="user@example.com"),
                                        "full_name": openapi.Schema(type="string", example="John Doe"),
                                        "age": openapi.Schema(type="integer", example=30),
                                        "sex": openapi.Schema(type="string", example="Male"),
                                    }
                                ),
                                "diagnosis": openapi.Schema(
                                    type="object",
                                    properties={
                                        "id": openapi.Schema(type="integer", example=1),
                                        "name": openapi.Schema(type="string", example="Flu"),
                                        "description": openapi.Schema(type="string", example="A common viral infection."),
                                        "symptoms": openapi.Schema(
                                            type="array",
                                            items=openapi.Schema(
                                                type="object",
                                                properties={
                                                    "id": openapi.Schema(type="integer", example=1),
                                                    "name": openapi.Schema(type="string", example="Fever"),
                                                    "description": openapi.Schema(type="string", example="Increased body temperature."),
                                                }
                                            )
                                        ),
                                        "created_at": openapi.Schema(type="string", format="date-time"),
                                        "updated_at": openapi.Schema(type="string", format="date-time"),
                                    }
                                ),
                                "drugs_recommended": openapi.Schema(
                                    type="array",
                                    items=openapi.Schema(
                                        type="object",
                                        properties={
                                            "id": openapi.Schema(type="integer", example=1),
                                            "name": openapi.Schema(type="string", example="Paracetamol"),
                                            "description": openapi.Schema(type="string", example="Pain reliever and a fever reducer."),
                                            "ADR_History": openapi.Schema(type="string", example="Nausea, Rash"),
                                            "created_at": openapi.Schema(type="string", format="date-time"),
                                            "updated_at": openapi.Schema(type="string", format="date-time"),
                                        }
                                    )
                                ),
                                "adr_history": openapi.Schema(
                                    type="array",
                                    items=openapi.Schema(
                                        type="object",
                                        properties={
                                            "drug_name": openapi.Schema(type="string", example="Aspirin"),
                                            "ADR_History": openapi.Schema(type="string", example="Gastrointestinal bleeding, Allergic reactions"),
                                        }
                                    )
                                ),
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
        serializer = PatientReportSerializer(data=request.data)
        if serializer.is_valid():
            existing_report = PatientReport.objects.filter(patient=request.user).first()
            
            if existing_report:
                existing_report.age = serializer.validated_data['age']
                existing_report.sex = serializer.validated_data['sex']
                existing_report.symptoms.set(serializer.validated_data['symptoms'])
                existing_report.save()
                report = existing_report
            else:
                report = serializer.save(patient=request.user)

            # Get all matching diagnoses based on symptoms
            matched_diagnoses = Diagnosis.objects.filter(symptoms__in=report.symptoms.all()).distinct()

            # Dictionary to count matching symptoms for each diagnosis
            symptom_count = {}
            for diagnosis in matched_diagnoses:
                count = diagnosis.symptoms.filter(id__in=report.symptoms.all()).count()
                symptom_count[diagnosis] = count

            # Find the diagnosis with the most matching symptoms
            best_diagnosis = max(symptom_count, key=symptom_count.get, default=None)

            report.diagnosis = best_diagnosis
            report.save()

            # Fetch drugs related to the best diagnosis
            drugs_recommended = Drug.objects.filter(symptoms__in=report.symptoms.all()).distinct()
            adr_history = [{"drug_name": drug.name, "ADR_History": drug.ADR_History} for drug in drugs_recommended]

            return success_response(
                message="Diagnosis generated successfully.",
                data={
                    "patient_info": {
                        "email": request.user.email,
                        "full_name": request.user.get_full_name(),
                        "age": report.age,
                        "sex": report.sex
                    },
                    "diagnosis": DiagnosisSerializer(best_diagnosis).data if best_diagnosis else None,
                    "drugs_recommended": DrugSerializer(drugs_recommended, many=True).data,
                    "adr_history": adr_history,
                },
                status_code=status.HTTP_201_CREATED
            )

        return error_response(
            message="Invalid data.",
            validation_errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
###################################################################################################################################


############################## SymptomListAPIView ###########################################################
class SymptomListAPIView(APIView):
    permission_classes = [IsUser]

    @swagger_auto_schema(
        tags=["Patient Diagnosis Management"],
        operation_summary="List all Symptoms",
        operation_description="Retrieve a list of all available symptoms.",
        responses={
            200: openapi.Response(
                description="List of symptoms retrieved successfully.",
                schema=SymptomSerializer(many=True)
            ),
            404: openapi.Response(description="Symptoms not found"),
        }
    )
    def get(self, request, *args, **kwargs):
        symptoms = Symptom.objects.all()

        if not symptoms.exists():
            return error_response("Symptoms not found", status_code=status.HTTP_404_NOT_FOUND)

        serializer = SymptomSerializer(symptoms, many=True)
        return success_response("List of symptoms retrieved successfully", data=serializer.data, count=symptoms.count())
###################################################################################################################################


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
        # Fetch the most recent reports, limit to the last 5
        reports = PatientReport.objects.filter(patient=request.user).order_by('-created_at')[:5]

        if not reports.exists():
            return error_response("No report history found", status_code=status.HTTP_404_NOT_FOUND)

        report_data = [
            {
                "id": report.id,
                "created_at": report.created_at,
                "updated_at": report.updated_at,
                
                "diagnosis": report.diagnosis.name if report.diagnosis else "Not diagnosed",
                "age": report.age,
                "sex": report.sex,
            }
            for report in reports
        ]

        return success_response(
            message="Recent report history retrieved successfully.",
            data=report_data,
            status_code=status.HTTP_200_OK
        )
###################################################################################################################################