from django.urls import path
from . import views

urlpatterns = [
   path('report-diagnosis/', views.ReportDiagnosisAPIView.as_view(), name='report-diagnosis'),
   path('symptoms/', views.SymptomListAPIView.as_view(), name='symptom-list'),
   path('report-history/', views.ReportHistoryAPIView.as_view(), name='report-history'),
]
