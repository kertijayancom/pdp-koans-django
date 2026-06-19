from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
import re

from koans.k01_data_minimization.models import UserProfile
from koans.k02_explicit_consent.models import ConsentLog
from koans.k05_data_portability.models import UserTransaction
from koans.k07_deletion_anonymisation.models import DeletionRequest

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

    def test_01_unauthenticated_access_denied(self):
        """Koan 07: Deletion request must require authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.delete(self.url)
        status_code = response.status_type if hasattr(response, 'status_type') else response.status_code
        self.assertIn(status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_02_basic_hard_delete(self):
        """[Basic] Koan 07A: Memastikan data identitas utama (User, Profile, ConsentLog) berhasil dihapus permanen"""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Cek User dan User Profile terhapus secara fisik
        self.assertFalse(User.objects.filter(email=self.email).exists())
        self.assertFalse(UserProfile.objects.filter(email=self.email).exists())

        # Cek Consent Log terhapus secara fisik
        self.assertFalse(ConsentLog.objects.filter(user_email=self.email).exists())

    def test_03_intermediate_deletion_and_anonymisation(self):
        """[Intermediate] Koan 07B: Memastikan data transaksi historis tetap utuh tetapi dianonimkan dengan format yang benar"""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Total transaksi di database harus tetap 3 (2 milik Jane + 1 milik orang lain)
        tx_count = UserTransaction.objects.count()
        self.assertEqual(tx_count, 3)

        self.tx1.refresh_from_db()
        self.tx2.refresh_from_db()
        self.other_tx.refresh_from_db()

        # Transaksi orang lain tidak boleh berubah
        self.assertEqual(self.other_tx.user_email, "other.user@example.com")

        # Transaksi Jane tidak boleh lagi menggunakan email aslinya
        self.assertNotEqual(self.tx1.user_email, self.email)
        self.assertNotEqual(self.tx2.user_email, self.email)

        # Pastikan format email anonim sesuai regex pattern
        email_pattern = re.compile(r'^anonymous_user_[a-zA-Z0-9\-]+@pdp\.local$')
        self.assertTrue(email_pattern.match(self.tx1.user_email), f"Email {self.tx1.user_email} tidak cocok dengan pola anonimisasi.")
        self.assertTrue(email_pattern.match(self.tx2.user_email), f"Email {self.tx2.user_email} tidak cocok dengan pola anonimisasi.")

    def test_04_advanced_delayed_deletion_trigger(self):
        """[Advanced] Koan 07C: Request dengan parameter delayed=true menonaktifkan user dan mencatat permintaan ekspor asinkron"""
        url_delayed = f"{self.url}?delayed=true"
        response = self.client.delete(url_delayed)
        
        self.assertEqual(
            response.status_code,
            status.HTTP_202_ACCEPTED,
            msg="Request dengan parameter delayed=true seharusnya mengembalikan status HTTP 202 Accepted!"
        )
        
        # User harus dinonaktifkan (soft delete) agar tidak bisa login/akses sistem
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active, msg="User yang meminta penghapusan tertunda harus dinonaktifkan (is_active = False)!")

        # Pastikan permintaan terekam di tabel DeletionRequest database
        request_exists = DeletionRequest.objects.filter(user_email=self.email, status='PENDING').exists()
        self.assertTrue(request_exists, msg="Permintaan penghapusan tertunda tidak tercatat di database DeletionRequest!")

        # Data fisik profil dan transaksi harus tetap ada (belum terhapus sinkron)
        self.assertTrue(UserProfile.objects.filter(email=self.email).exists())
        self.assertEqual(UserTransaction.objects.filter(user_email=self.email).count(), 2)
