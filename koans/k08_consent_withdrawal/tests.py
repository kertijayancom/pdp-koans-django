from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from koans.k02_explicit_consent.models import ConsentLog
from koans.k08_consent_withdrawal.models import RevokedToken

User = get_user_model()

class ConsentWithdrawalTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.email = "john.doe@example.com"
        self.username = "johndoe"
        self.password = "SecurePassword123!"
        
        # Create User
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )
        
        # Initially they have given consent
        self.initial_consent = ConsentLog.objects.create(
            user_email=self.email,
            consent_given=True,
            ip_address="192.168.1.1",
            policy_version="v1.0"
        )
        
        self.url = reverse('pdp-withdraw-consent')
        self.client.force_authenticate(user=self.user)

    def test_01_unauthenticated_access_denied(self):
        """Koan 08: Consent withdrawal request must require authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, {"policy_version": "v1.0"})
        status_code = response.status_type if hasattr(response, 'status_type') else response.status_code
        self.assertIn(status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_02_basic_consent_withdrawal_success(self):
        """[Basic/Intermediate] Koan 08A/B: Penarikan persetujuan berhasil mencatat log withdrawal dan menonaktifkan akun"""
        response = self.client.post(self.url, {"policy_version": "v1.1"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 1. Verifikasi log baru tersimpan (consent_given = False)
        logs = ConsentLog.objects.filter(user_email=self.email).order_by('-timestamp')
        self.assertEqual(logs.count(), 2)
        
        latest_log = logs.first()
        self.assertFalse(latest_log.consent_given)
        self.assertEqual(latest_log.policy_version, "v1.1")

        # 2. Verifikasi user dinonaktifkan
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_03_advanced_session_revocation(self):
        """[Advanced] Koan 08C: Menambahkan token JTI ke database pencabutan sesi (blacklist) saat penarikan persetujuan"""
        response = self.client.post(self.url, {
            "policy_version": "v1.1",
            "token_jti": "jti_jwt_token_session_abc123"
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifikasi token masuk ke daftar blacklist database
        token_revoked = RevokedToken.objects.filter(
            user_email=self.email,
            token_jti="jti_jwt_token_session_abc123"
        ).exists()
        self.assertTrue(token_revoked, msg="Token JTI yang ditarik tidak terdaftar di database RevokedToken!")
