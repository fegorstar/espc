from django.urls import path
from . import views

urlpatterns = [
     path('adr/report/', views.ReportADRAPIView.as_view(), name='report_adr'),
    
]
