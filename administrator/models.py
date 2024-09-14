from accounts.models import User
from django.db import models


class Drug(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    side_effects = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ADRReport(models.Model):
    patient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='adr_reports')
    drug = models.ForeignKey(
        Drug, on_delete=models.CASCADE, related_name='adr_reports')
    symptoms = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ADR Report by {self.patient.get_full_name()} on {self.drug.name}"


class Symptom(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Diagnosis(models.Model):
    name = models.CharField(max_length=255)
    symptoms = models.ManyToManyField(Symptom, related_name='diagnoses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
