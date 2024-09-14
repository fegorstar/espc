from django.contrib import admin
from .models import Drug, ADRReport, Symptom, Diagnosis


class DrugAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'side_effects',
                    'created_at', 'updated_at')
    search_fields = ('name', 'description', 'side_effects')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)


class ADRReportAdmin(admin.ModelAdmin):
    list_display = ('patient', 'drug', 'symptoms', 'created_at', 'updated_at')
    search_fields = ('patient__email', 'drug__name', 'symptoms')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)


class SymptomAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')
    ordering = ('name',)


class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')
    ordering = ('name',)


admin.site.register(Drug, DrugAdmin)
admin.site.register(ADRReport, ADRReportAdmin)
admin.site.register(Symptom, SymptomAdmin)
admin.site.register(Diagnosis, DiagnosisAdmin)
