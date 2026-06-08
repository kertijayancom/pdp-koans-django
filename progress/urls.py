from django.urls import path
from progress.views import ProgressView
from koans.k02_explicit_consent.views import RegisterWithConsentView
from koans.k04_rbac_audit.views import CustomerSensitiveDataView

urlpatterns = [
    path('progress/', ProgressView.as_view(), name='pdp-progress'),
    path('register/', RegisterWithConsentView.as_view(), name='pdp-register'),
    path('customers/<str:id>/sensitive/', CustomerSensitiveDataView.as_view(), name='pdp-sensitive'),
]
