from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from koans.k01_data_minimization.models import UserProfile
from koans.k09_purpose_limitation.models import GranularMarketingConsent
from koans.k06_breach_response.models import CompromisedUser

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

    def test_01_basic_marketing_dispatch_filters_by_general_consent(self):
        """[Basic] Koan 09A: Hanya admin yang bisa memicu dispatch, dan daftar disaring berdasarkan general consent"""
        # Pengguna non-admin ditolak
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Pengguna admin berhasil
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        recipients = response.data["recipients"]
        self.assertIn("optin@example.com", recipients)
        self.assertNotIn("optout@example.com", recipients)
        self.assertEqual(len(recipients), 1)

    def test_02_intermediate_marketing_dispatch_by_granular_category(self):
        """[Intermediate] Koan 09B: Penyaringan penerima newsletter berdasarkan kategori persetujuan granular (granular consent)"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Daftarkan persetujuan granular untuk kampanye 'weekly_newsletter'
        GranularMarketingConsent.objects.create(
            user_email="optin@example.com",
            category="weekly_newsletter",
            consent_given=True
        )
        GranularMarketingConsent.objects.create(
            user_email="optout@example.com",
            category="weekly_newsletter",
            consent_given=False
        )
        
        # Kirim kampanye kategori 'weekly_newsletter'
        response = self.client.post(self.url, {"category": "weekly_newsletter"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        recipients = response.data["recipients"]
        self.assertIn("optin@example.com", recipients)
        self.assertNotIn("optout@example.com", recipients)
        self.assertEqual(len(recipients), 1)

    def test_03_advanced_marketing_dispatch_excludes_inactive_or_compromised(self):
        """[Advanced] Koan 09C: Menolak pengiriman promosi kepada pengguna tidak aktif atau akunnya terkompromi/diretas"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Daftarkan user baru dengan consent=True
        User.objects.create_user(
            username="inactive_user",
            email="inactive@example.com",
            password="SecurePassword123!"
        )
        UserProfile.objects.create(
            username="inactive_user",
            email="inactive@example.com",
            phone_number="08144444444",
            shipping_address="Malang",
            marketing_consent=True
        )
        
        # Ubah status user tersebut menjadi tidak aktif (is_active = False)
        django_user = User.objects.get(email="inactive@example.com")
        django_user.is_active = False
        django_user.save()
        
        # Daftarkan user lain dengan consent=True tapi ditandai compromised di database
        User.objects.create_user(
            username="compromised_user",
            email="compromised@example.com",
            password="SecurePassword123!"
        )
        UserProfile.objects.create(
            username="compromised_user",
            email="compromised@example.com",
            phone_number="08155555555",
            shipping_address="Solo",
            marketing_consent=True
        )
        CompromisedUser.objects.create(
            user_email="compromised@example.com",
            is_compromised=True
        )

        # Dispatch kampanye (default general consent)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        recipients = response.data["recipients"]
        
        # Hanya 'optin@example.com' yang aktif & aman yang boleh menerima
        self.assertIn("optin@example.com", recipients)
        
        # User tidak aktif (inactive@example.com) disaring keluar
        self.assertNotIn("inactive@example.com", recipients)
        
        # User terkompromi (compromised@example.com) disaring keluar
        self.assertNotIn("compromised@example.com", recipients)
        
        # Total penerima tetap 1
        self.assertEqual(len(recipients), 1)
