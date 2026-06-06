from django.urls import path
from progress.views import ProgressView
from koans.k02_explicit_consent.views import RegisterWithConsentView

urlpatterns = [
    path('progress/', ProgressView.as_view(), name='pdp-progress'),
    path('register/', RegisterWithConsentView.as_view(), name='pdp-register'),
]
