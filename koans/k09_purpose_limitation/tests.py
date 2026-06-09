from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from koans.k01_data_minimization.models import UserProfile

User = get_user_model()

class PurposeLimitationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create an Admin User (Staf Marketing)
        self.admin_user = User.objects.create_superuser(
            username="admin_marketing",
            email="admin@pdp.local",
            password="SecurePassword123!"
        )
        
        # Create a Regular User
        self.regular_user = User.objects.create_user(
            username="regular_user",
            email="regular@example.com",
            password="SecurePassword123!"
        )
        
        # 1. Profile with explicit marketing consent (opted-in)
        self.profile_with_consent = UserProfile.objects.create(
            username="user_opt_in",
            email="optin@example.com",
            phone_number="08122222222",
            shipping_address="Bandung, Indonesia",
            marketing_consent=True
        )
        
        # 2. Profile without marketing consent (opted-out)
        self.profile_no_consent = UserProfile.objects.create(
            username="user_opt_out",
            email="optout@example.com",
            phone_number="08133333333",
            shipping_address="Surabaya, Indonesia",
            marketing_consent=False
        )

        self.url = reverse('pdp-marketing-dispatch')

    def test_non_admin_access_denied(self):
        """Koan 09: Marketing dispatch must be restricted to admin/staff users"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(self.url)
        status_code = response.status_type if hasattr(response, 'status_type') else response.status_code
        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN)

    def test_marketing_dispatch_filters_by_purpose_consent(self):
        """Koan 09: Dispatch list must only include users who consented to marketing"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("recipients", response.data)
        
        recipients = response.data["recipients"]
        
        # Must contain the user who opted-in
        self.assertIn("optin@example.com", recipients)
        
        # Must NOT contain the user who did not opt-in
        self.assertNotIn("optout@example.com", recipients)
        
        # Total recipients should be exactly 1
        self.assertEqual(len(recipients), 1)
