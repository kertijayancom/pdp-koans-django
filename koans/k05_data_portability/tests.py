from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from koans.k01_data_minimization.models import UserProfile
from koans.k02_explicit_consent.models import ConsentLog
from koans.k05_data_portability.models import UserTransaction, DataExportJob

class DataPortabilityTestCase(APITestCase):

    def setUp(self):
        # User 1 (Penguji/Pemilik Akun)
        self.user = User.objects.create_user(
            username="user_portabilitas",
            email="portabilitas@example.com",
            password="password_aman"
        )
        
        # Buat profile untuk User 1
        self.profile = UserProfile.objects.create(
            username=self.user.username,
            email=self.user.email,
            phone_number="081234567890",
            shipping_address="Bandung"
        )
        
        # Buat Log Consent untuk User 1
        self.consent = ConsentLog.objects.create(
            user_email=self.user.email,
            consent_given=True,
            ip_address="192.168.1.1",
            policy_version="v1.5"
        )
        
        # Buat Log Transaksi untuk User 1
        self.transaction_1 = UserTransaction.objects.create(
            user_email=self.user.email,
            item_name="Buku Rekayasa Perangkat Lunak",
            amount=125000.00
        )
        self.transaction_2 = UserTransaction.objects.create(
            user_email=self.user.email,
            item_name="Sepatu Olahraga",
            amount=450000.00
        )

        # User 2 (Korban/Target IDOR)
        self.other_user = User.objects.create_user(
            username="korban_idor",
            email="korban@example.com",
            password="password_korban"
        )
        self.other_profile = UserProfile.objects.create(
            username=self.other_user.username,
            email=self.other_user.email,
            phone_number="089999999999",
            shipping_address="Jakarta"
        )

    def test_01_basic_prevent_idor_attacks(self):
        """[Basic] Koan 5A: Memastikan sistem memblokir serangan IDOR/BOLA (HTTP 403) jika user mencoba mengekspor data orang lain"""
        self.client.force_authenticate(user=self.user)
        
        # Coba eksploitasi URL dengan menyisipkan email User 2 (korban) lewat query parameter
        url = f'/api/users/export-data/?email={self.other_user.email}'
        response = self.client.get(url)
        
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            msg="Celah IDOR/BOLA terdeteksi! User diizinkan memicu ekspor atau mengintip data email milik user lain lewat parameter."
        )

    def test_02_intermediate_successful_export_format(self):
        """[Intermediate] Koan 5B: Memastikan ekspor data sukses (HTTP 200) dengan isi agregasi data lengkap dari 3 tabel"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/users/export-data/')
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg="Gagal mengakses endpoint ekspor portabilitas data pribadi!"
        )
        
        data = response.data
        
        # Verifikasi data profil
        self.assertIn("profile", data, msg="Skema JSON ekspor harus memiliki field 'profile'")
        self.assertEqual(
            data["profile"]["phone_number"], 
            self.profile.phone_number,
            msg="Data nomor telepon profil di hasil ekspor tidak cocok atau tidak ditemukan!"
        )
        
        # Verifikasi data consent
        self.assertIn("consent_logs", data, msg="Skema JSON ekspor harus memiliki field 'consent_logs'")
        self.assertTrue(
            len(data["consent_logs"]) >= 1,
            msg="Riwayat log persetujuan (ConsentLog) pengguna tidak termuat dalam hasil ekspor!"
        )
        self.assertEqual(
            data["consent_logs"][0]["policy_version"], 
            "v1.5",
            msg="Detail data consent_logs pada hasil ekspor tidak akurat!"
        )
        
        # Verifikasi data transaksi
        self.assertIn("transactions", data, msg="Skema JSON ekspor harus memiliki field 'transactions'")
        self.assertEqual(
            len(data["transactions"]), 
            2,
            msg="Jumlah riwayat transaksi yang diekspor tidak sesuai (seharusnya 2 transaksi)!"
        )

    def test_03_advanced_async_export_trigger(self):
        """[Advanced] Koan 5C: Memastikan request dengan async=true menghasilkan HTTP 202 Accepted dan DataExportJob baru"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/users/export-data/?async=true')
        self.assertEqual(
            response.status_code,
            status.HTTP_202_ACCEPTED,
            msg="Request dengan parameter async=true seharusnya mengembalikan status HTTP 202 Accepted!"
        )
        
        self.assertIn("job_id", response.data, msg="Response async export harus mengembalikan 'job_id'")
        self.assertEqual(response.data["status"], "PENDING", msg="Status awal job baru harus 'PENDING'")
        
        # Pastikan data tersimpan di database
        job_exists = DataExportJob.objects.filter(id=response.data["job_id"]).exists()
        self.assertTrue(job_exists, msg="DataExportJob tidak tersimpan di database!")

    def test_04_advanced_async_export_polling(self):
        """[Advanced] Koan 5D: Menguji endpoint polling status pekerjaan ekspor data"""
        self.client.force_authenticate(user=self.user)
        
        # Buat dummy job terlebih dahulu
        job = DataExportJob.objects.create(
            user_email=self.user.email,
            status="PENDING"
        )
        
        # Polling status pekerjaan ekspor
        url = f'/api/users/export-data/?job_id={job.id}'
        response = self.client.get(url)
        
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg="Endpoint polling status pekerjaan ekspor harus mengembalikan HTTP 200 OK!"
        )
        
        # Verifikasi data
        self.assertEqual(response.data["status"], "COMPLETED", msg="Pekerjaan ekspor yang di-polling harus berubah menjadi COMPLETED")
        self.assertIsNotNone(response.data["download_url"], msg="Hasil polling harus menyertakan download_url")
