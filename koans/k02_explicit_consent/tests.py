from rest_framework.test import APITestCase
from rest_framework import status
from koans.k02_explicit_consent.models import ConsentLog

class ExplicitConsentTestCase(APITestCase):
    
    def test_01_reject_without_consent(self):
        """Koan 2A: Memastikan sistem menolak registrasi jika user tidak memberikan persetujuan (consent_given=False)"""
        url = '/api/register/' # Note: we don't have to define global URL pattern if we test the view directly, but we registered it, or we can use the view APIClient request
        # To avoid dependency on root urls.py configuration, let's call the view directly using APIRequestFactory or self.client
        # If urls.py is configured correctly, self.client works. Let's register /api/register/ in progress/urls.py or core/urls.py to make tests reliable.
        # Actually, let's register the URL in progress/urls.py since we included progress.urls under /api/.
        
        response = self.client.post('/api/register/', {
            "email": "user@example.com",
            "consent_given": False,
            "policy_version": "v1.0"
        }, format='json')
        
        self.assertEqual(
            response.status_code, 
            status.HTTP_400_BAD_REQUEST,
            msg="Sistem meloloskan registrasi tanpa explicit consent! Seharusnya mengembalikan HTTP 400 Bad Request."
        )

    def test_02_accept_and_log_consent(self):
        """Koan 2B: Memastikan sistem mencatat persetujuan user ke log audit (pdp_consent_logs) saat registrasi berhasil"""
        test_email = "sukses@example.com"
        test_version = "v2.0"
        
        response = self.client.post('/api/register/', {
            "email": test_email,
            "consent_given": True,
            "policy_version": test_version
        }, format='json')
        
        self.assertEqual(
            response.status_code, 
            status.HTTP_201_CREATED,
            msg="Registrasi gagal dengan consent yang valid! Seharusnya mengembalikan HTTP 201 Created."
        )
        
        # Check if record is inserted in the database
        log_exists = ConsentLog.objects.filter(
            user_email=test_email, 
            consent_given=True,
            policy_version=test_version
        ).exists()
        
        self.assertTrue(
            log_exists,
            msg="Persetujuan berhasil tetapi log audit (ConsentLog) tidak tersimpan di database! Ini melanggar Pasal 21 UU PDP (bukti persetujuan)."
        )
