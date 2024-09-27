from rest_framework import serializers
from .models import Drug, Symptom, Diagnosis, PatientReport


class SymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptom
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']


class DiagnosisSerializer(serializers.ModelSerializer):
    symptoms = SymptomSerializer(many=True, read_only=True)

    class Meta:
        model = Diagnosis
        fields = ['id', 'name', 'description', 'symptoms', 'created_at', 'updated_at']


class DrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drug
        fields = ['id', 'name', 'description', 'ADR_History', 'created_at', 'updated_at']


class PatientReportSerializer(serializers.ModelSerializer):
    symptoms = serializers.PrimaryKeyRelatedField(queryset=Symptom.objects.all(), many=True)

    class Meta:
        model = PatientReport
        fields = ['id', 'patient', 'age', 'sex', 'symptoms', 'diagnosis', 'drugs_recommended', 'created_at', 'updated_at']
        read_only_fields = ['patient', 'diagnosis', 'drugs_recommended', 'created_at', 'updated_at']
        