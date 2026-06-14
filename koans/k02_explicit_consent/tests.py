from rest_framework.test import APITestCase
from rest_framework import status
from koans.k02_explicit_consent.models import ConsentLog
from koans.k01_data_minimization.models import UserProfile

class ExplicitConsentTestCase(APITestCase):
    
    def test_01_reject_without_consent(self):
        """[Basic] Koan 2A: Memastikan sistem menolak registrasi jika user tidak memberikan persetujuan layanan utama (consent_service=False)"""
        response = self.client.post('/api/register/', {
            "email": "user@example.com",
            "consent_service": False,
            "consent_marketing": False,
            "policy_version": "v1.0"
        }, format='json')
        
        self.assertEqual(
            response.status_code, 
            status.HTTP_400_BAD_REQUEST,
            msg="Sistem meloloskan registrasi tanpa explicit consent layanan utama! Seharusnya mengembalikan HTTP 400 Bad Request."
        )

    def test_02_accept_and_log_consent(self):
        """[Intermediate] Koan 2B: Memastikan sistem mencatat persetujuan ke log audit (pdp_consent_logs) saat registrasi berhasil"""
        test_email = "sukses@example.com"
        test_version = "v2.0"
        
        response = self.client.post('/api/register/', {
            "email": test_email,
            "consent_service": True,
            "consent_marketing": False,
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

    def test_03_consent_unbundling_success(self):
        """[Advanced] Koan 2C: Memastikan registrasi tetap sukses jika menolak persetujuan marketing (unbundling consent)"""
        test_email = "unbundled@example.com"
        
        response = self.client.post('/api/register/', {
            "email": test_email,
            "consent_service": True,
            "consent_marketing": False,
            "policy_version": "v1.0"
        }, format='json')
        
        self.assertEqual(
            response.status_code, 
            status.HTTP_201_CREATED,
            msg="Registrasi ditolak karena user tidak menyetujui marketing! Ini melanggar aturan unbundling consent (Pasal 20 UU PDP jo. RPP Pasal 55)."
        )
        
        # Verify that UserProfile is created but marketing_consent is False
        profile = UserProfile.objects.get(email=test_email)
        self.assertFalse(
            profile.marketing_consent,
            msg="UserProfile terbuat tetapi marketing_consent harus bernilai False karena user tidak menyetujui promo marketing!"
        )

    def test_04_consent_unbundling_marketing_granted(self):
        """[Advanced] Koan 2D: Memastikan registrasi sukses dan marketing_consent aktif jika menyetujui promo marketing"""
        test_email = "optin@example.com"
        
        response = self.client.post('/api/register/', {
            "email": test_email,
            "consent_service": True,
            "consent_marketing": True,
            "policy_version": "v1.0"
        }, format='json')
        
        self.assertEqual(
            response.status_code, 
            status.HTTP_201_CREATED,
            msg="Registrasi gagal dengan seluruh consent bernilai True!"
        )
        
        # Verify that UserProfile is created and marketing_consent is True
        profile = UserProfile.objects.get(email=test_email)
        self.assertTrue(
            profile.marketing_consent,
            msg="UserProfile terbuat tetapi marketing_consent harus bernilai True karena user menyetujui promo marketing!"
        )
