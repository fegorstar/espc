from django.db import models
from accounts.models import User
from rest_framework import serializers
from .models import Drug, ADRReport, Diagnosis,Symptom


class DrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drug
        fields = ['id', 'name', 'description',
                  'side_effects', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ADRReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ADRReport
        fields = ['id', 'patient', 'drug',
                  'symptoms', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class SymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptom
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class DiagnosisSerializer(serializers.ModelSerializer):
    symptoms = SymptomSerializer(many=True)

    class Meta:
        model = Diagnosis
        fields = ['id', 'name', 'symptoms', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        symptoms_data = validated_data.pop('symptoms')
        diagnosis = Diagnosis.objects.create(**validated_data)
        for symptom_data in symptoms_data:
            symptom, created = Symptom.objects.get_or_create(**symptom_data)
            diagnosis.symptoms.add(symptom)
        return diagnosis

    def update(self, instance, validated_data):
        symptoms_data = validated_data.pop('symptoms')
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        # Clear existing symptoms and add the new ones
        instance.symptoms.clear()
        for symptom_data in symptoms_data:
            symptom, created = Symptom.objects.get_or_create(**symptom_data)
            instance.symptoms.add(symptom)
        
        return instance