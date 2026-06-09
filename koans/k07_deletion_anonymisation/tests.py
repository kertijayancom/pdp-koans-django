from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
import re

from koans.k01_data_minimization.models import UserProfile
from koans.k02_explicit_consent.models import ConsentLog
from koans.k05_data_portability.models import UserTransaction

User = get_user_model()

class DataDeletionAnonymisationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.email = "jane.doe@example.com"
        self.username = "janedoe"
        self.password = "SecurePassword123!"
        
        # Create User
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )
        
        # Create User Profile
        self.profile = UserProfile.objects.create(
            username=self.username,
            email=self.email,
            phone_number="081234567890",
            shipping_address="Jakarta, Indonesia"
        )
        
        # Create Consent Logs
        self.consent_log = ConsentLog.objects.create(
            user_email=self.email,
            consent_given=True,
            ip_address="192.168.1.1",
            policy_version="v1.0"
        )
        
        # Create User Transactions
        self.tx1 = UserTransaction.objects.create(
            user_email=self.email,
            item_name="E-book: Privacy Matters",
            amount=99000.00
        )
        self.tx2 = UserTransaction.objects.create(
            user_email=self.email,
            item_name="Privacy Protection Sticker Set",
            amount=25000.00
        )
        
        # Another user's transactions to ensure we don't anonymize others
        self.other_tx = UserTransaction.objects.create(
            user_email="other.user@example.com",
            item_name="Random Item",
            amount=50000.00
        )

        self.url = reverse('pdp-delete')
        self.client.force_authenticate(user=self.user)

    def test_unauthenticated_access_denied(self):
        """Koan 07: Deletion request must require authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.delete(self.url)
        status_code = response.status_type if hasattr(response, 'status_type') else response.status_code
        self.assertIn(status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


    def test_account_deletion_and_anonymisation(self):
        """Koan 07: Deleting account hard-deletes user info but anonymizes transaction logs"""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 1. Check user and user profile are hard-deleted
        self.assertFalse(User.objects.filter(email=self.email).exists())
        self.assertFalse(UserProfile.objects.filter(email=self.email).exists())

        # 2. Check consent logs are hard-deleted
        self.assertFalse(ConsentLog.objects.filter(user_email=self.email).exists())

        # 3. Check transactions are NOT deleted but anonymized
        tx_count = UserTransaction.objects.count()
        # Total transactions (2 from Jane + 1 from other) must still be 3
        self.assertEqual(tx_count, 3)

        # Verify Jane's transactions are anonymized
        self.tx1.refresh_from_db()
        self.tx2.refresh_from_db()
        self.other_tx.refresh_from_db()

        # The other user's transaction must remain intact
        self.assertEqual(self.other_tx.user_email, "other.user@example.com")

        # Jane's transactions must now have anonymous_user_xxxx@pdp.local
        self.assertNotEqual(self.tx1.user_email, self.email)
        self.assertNotEqual(self.tx2.user_email, self.email)

        # Match format 'anonymous_user_xxxx@pdp.local'
        email_pattern = re.compile(r'^anonymous_user_[a-zA-Z0-9\-]+@pdp\.local$')
        self.assertTrue(email_pattern.match(self.tx1.user_email), f"Email {self.tx1.user_email} does not match anonymisation pattern.")
        self.assertTrue(email_pattern.match(self.tx2.user_email), f"Email {self.tx2.user_email} does not match anonymisation pattern.")

        # Ensure the random parts are unique/stable per operation or consistent
        self.assertIsNotNone(self.tx1.user_email)
