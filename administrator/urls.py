from django.urls import path
from . import views

urlpatterns = [
   path('report-diagnosis/', views.ReportDiagnosisAPIView.as_view(), name='report-diagnosis'),
   path('symptoms/', views.SymptomListAPIView.as_view(), name='symptom-list'),
   path('report-history/', views.ReportHistoryAPIView.as_view(), name='report-history'),
   path('check-drug-safety/', views.CheckDrugSafetyAPIView.as_view(), name='check-drug-safety'),
   path('side-effect-questions/', views.SideEffectQuestionsAPIView.as_view(), name='side-effect-questions'),
]
