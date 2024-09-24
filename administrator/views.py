from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import DiagnosisSerializer, PatientReportSerializer, DrugSerializer, SymptomSerializer
from .models import Diagnosis, Drug, PatientReport, Symptom, DrugQuestion, DrugQuestionOption
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


############################## SideEffectQuestionsAPIView ###########################################################
class SideEffectQuestionsAPIView(APIView):
    permission_classes = [IsUser]

    @swagger_auto_schema(
        tags=["Drug Management"],
        operation_summary="Retrieve Drug Side Effects Questions",
        operation_description="Fetch questions about drugs and their associated side effects.",
        responses={
            200: openapi.Response(
                description="Drug side effects questions retrieved successfully.",
                schema=openapi.Schema(
                    type="object",
                    properties={
                        "status": openapi.Schema(type="integer", example=200),
                        "message": openapi.Schema(type="string", example="Drug side effects questions retrieved successfully."),
                        "data": openapi.Schema(
                            type="array",
                            items=openapi.Schema(
                                type="object",
                                properties={
                                    "drug_id": openapi.Schema(type="integer", example=1),
                                    "drug_name": openapi.Schema(type="string", example="Paracetamol"),
                                    "questions": openapi.Schema(
                                        type="array",
                                        items=openapi.Schema(
                                            type="object",
                                            properties={
                                                "question_id": openapi.Schema(type="integer", example=1),
                                                "question_text": openapi.Schema(type="string", example="What are the common side effects?"),
                                                "options": openapi.Schema(
                                                    type="array",
                                                    items=openapi.Schema(type="string", example="Nausea")
                                                )
                                            }
                                        )
                                    )
                                }
                            )
                        )
                    }
                )
            ),
            401: openapi.Response(description="Unauthorized")
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            # Fetch the latest PatientReport for the authenticated user
            patient_report = PatientReport.objects.filter(patient=request.user).last()
            
            if not patient_report or not patient_report.symptoms.exists():
                return error_response(
                    message="No symptoms found for the user.",
                    validation_errors={"error": "User has no associated symptoms."}
                )

            # Fetch drugs related to the symptoms from the patient's report
            recommended_drugs = Drug.objects.filter(symptoms__in=patient_report.symptoms.all()).distinct()

            # Prepare the data structure for questions about drugs and their side effects
            drug_data = []
            for drug in recommended_drugs:
                questions = DrugQuestion.objects.filter(drug=drug)
                question_data = []
                
                for question in questions:
                    options = DrugQuestionOption.objects.filter(question=question).values_list('option_text', flat=True)
                    question_data.append({
                        "question_id": question.id,
                        "question_text": question.question_text,
                        "options": list(options)
                    })
                
                drug_data.append({
                    "drug_id": drug.id,
                    "drug_name": drug.name,
                    "questions": question_data
                })

            return success_response(
                message="Drug side effects questions retrieved successfully.",
                data=drug_data
            )
        except Exception as e:
            return error_response(
                message="Failed to retrieve drug side effects questions.",
                validation_errors=str(e)
            )
################################################################################################################################### 
############################################# Helper Functions ###########################################################
class CheckDrugSafetyAPIView(APIView):
    permission_classes = [IsUser]

    @swagger_auto_schema(
        tags=["Drug Management"],
        operation_summary="Check Drug Safety Based on User Input for Each Drug",
        operation_description="This endpoint receives the user's side effect input for each drug and recommends drugs based on safety.",
        request_body=openapi.Schema(
            type="object",
            properties={
                "drug_side_effects": openapi.Schema(
                    type="object",
                    additional_properties=openapi.Schema(
                        type="array",
                        items=openapi.Items(type="string"),
                        example=["Nausea", "None of the Above"]
                    ),
                    example={
                        "1": ["Nausea", "Vomiting"],
                        "2": ["None of the Above"],
                        "3": ["Dizziness", "None of the Above"]
                    }
                )
            },
            required=["drug_side_effects"]
        ),
        responses={
            200: openapi.Response(
                description="Drug recommendations based on user input.",
                schema=openapi.Schema(
                    type="object",
                    properties={
                        "status": openapi.Schema(type="integer", example=200),
                        "message": openapi.Schema(type="string", example="Drug recommendation completed successfully."),
                        "data": openapi.Schema(
                            type="object",
                            properties={
                                "patient_full_name": openapi.Schema(type="string", example="John Doe"),
                                "age": openapi.Schema(type="integer", example=35),
                                "sex": openapi.Schema(type="string", example="Male"),
                                "drug_count": openapi.Schema(type="integer", example=3),
                                "drugs": openapi.Schema(type="array", items=openapi.Items(type="object"))
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
        drug_side_effects = request.data.get("drug_side_effects", {})

        if not drug_side_effects:
            return Response(
                {"message": "Drug side effects data is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get patient report tied to the authenticated user
        try:
            patient_report = PatientReport.objects.get(patient=request.user)
            full_name = f"{patient_report.patient.first_name} {patient_report.patient.last_name}"
            age = patient_report.age
            sex = patient_report.sex
        except PatientReport.DoesNotExist:
            return Response(
                {"message": "Patient report not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get drug recommendations based on the user's side effect input
        recommendation = self.recommend_drug_with_side_effects(drug_side_effects)

        all_drugs = recommendation.get("priority_drugs", [])

        # Serialize the drugs
        serialized_drugs = DrugSerializer(all_drugs, many=True).data if all_drugs else None

        return Response(
            {
                "status": 200,
                "message": "Drug recommendation completed successfully.",
                "data": {
                    "patient_full_name": full_name,
                    "age": age,
                    "sex": sex,
                    "drug_count": len(all_drugs),
                    "drugs": serialized_drugs
                }
            },
            status=status.HTTP_200_OK
        )

    def recommend_drug_with_side_effects(self, drug_side_effects):
        recommended_drugs = {
            "priority_drugs": []
        }

        for drug_id, side_effects in drug_side_effects.items():
            if "None of the Above" in side_effects:  # Only consider drugs with "None of the Above"
                try:
                    drug = Drug.objects.get(id=drug_id)
                    recommended_drugs["priority_drugs"].append(drug)

                except Drug.DoesNotExist:
                    continue

        return recommended_drugs
