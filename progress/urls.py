from django.urls import path
from progress.views import ProgressView
from koans.k02_explicit_consent.views import RegisterWithConsentView
from koans.k04_rbac_audit.views import CustomerSensitiveDataView
from koans.k05_data_portability.views import DataPortabilityExportView
from koans.k06_breach_response.views import SecureSensitiveResourceView, BreachNotificationReportView

urlpatterns = [
    path('progress/', ProgressView.as_view(), name='pdp-progress'),
    path('register/', RegisterWithConsentView.as_view(), name='pdp-register'),
    path('customers/<str:id>/sensitive/', CustomerSensitiveDataView.as_view(), name='pdp-sensitive'),
    path('users/export-data/', DataPortabilityExportView.as_view(), name='pdp-export'),
    path('resource/sensitive/', SecureSensitiveResourceView.as_view(), name='pdp-containment'),
    path('breach-report/', BreachNotificationReportView.as_view(), name='pdp-breach-report'),
]
