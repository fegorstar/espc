from django.contrib import admin
from .models import Symptom, Diagnosis, Drug, PatientReport, DrugQuestion, DrugQuestionOption

@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')  # Added 'id'
    search_fields = ('name',)

@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')  # Added 'id'
    search_fields = ('name',)
    filter_horizontal = ('symptoms',)

@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')  # Added 'id'
    search_fields = ('name',)
    filter_horizontal = ('symptoms',)

@admin.register(PatientReport)
class PatientReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'age', 'sex', 'created_at', 'updated_at')  # Added 'id'
    search_fields = ('patient__email',)
    list_filter = ('sex',)

@admin.register(DrugQuestion)
class DrugQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'drug', 'question_text')  # Added 'id'
    search_fields = ('question_text',)

@admin.register(DrugQuestionOption)
class DrugQuestionOptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'option_text')  # Added 'id'
    search_fields = ('option_text',)

# Optionally, you can customize the admin site title and header
admin.site.site_header = "Pharmacovigilance Admin"
admin.site.site_title = "Pharmacovigilance Admin Portal"
