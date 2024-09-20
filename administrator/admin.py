from django.contrib import admin
from .models import Drug, Symptom, Diagnosis, PatientReport


class SymptomInline(admin.TabularInline):
    model = Drug.symptoms.through
    extra = 1
    verbose_name = "Symptom"
    verbose_name_plural = "Symptoms"


class DrugAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'ADR_History', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'ADR_History')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    inlines = [SymptomInline]
    prepopulated_fields = {'description': ('name',)}  # Optional: Auto-fill description from name


class SymptomInlineDiagnosis(admin.TabularInline):
    model = Diagnosis.symptoms.through
    extra = 1
    verbose_name = "Symptom"
    verbose_name_plural = "Symptoms"


class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')
    ordering = ('name',)
    inlines = [SymptomInlineDiagnosis]
    prepopulated_fields = {'description': ('name',)}  # Optional: Auto-fill description from name


class PatientReportAdmin(admin.ModelAdmin):
    list_display = ('patient', 'age', 'sex', 'diagnosis', 'created_at', 'updated_at')
    search_fields = ('patient__email', 'age', 'sex')
    list_filter = ('created_at', 'updated_at', 'diagnosis', 'sex')
    ordering = ('-created_at',)
    raw_id_fields = ('patient',)  # Use raw ID field for better performance with large user base

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('diagnosis', 'patient')  # Optimize queries
        return queryset


class SymptomAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')
    ordering = ('name',)
    prepopulated_fields = {'description': ('name',)}  # Optional: Auto-fill description from name


admin.site.register(Drug, DrugAdmin)
admin.site.register(Symptom, SymptomAdmin)
admin.site.register(Diagnosis, DiagnosisAdmin)
admin.site.register(PatientReport, PatientReportAdmin)
