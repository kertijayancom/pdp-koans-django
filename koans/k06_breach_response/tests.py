from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from koans.k06_breach_response.models import IncidentReport, CompromisedUser

class BreachIncidentResponseTestCase(APITestCase):

    def setUp(self):
        # User 1: Akun aman
        self.secure_user = User.objects.create_user(
            username="secure_dev",
            email="secure@example.com",
            password="password_aman"
        )
        self.secure_user.is_compromised = False
        
        # User 2: Akun terkompromi/diretas (ditandai di Python attribute)
        self.compromised_user = User.objects.create_user(
            username="hacked_user",
            email="hacked@example.com",
            password="password_bocor"
        )
        self.compromised_user.is_compromised = True

        # Log Insiden Keamanan
        self.incident = IncidentReport.objects.create(
            root_cause="SQL Injection pada endpoint pencarian produk",
            impacted_subjects_count=1500,
            remediation_actions="Penutupan celah parameter query, penggantian token DB, dan reset password paksa untuk akun terdampak.",
            reported_to_bppa=False
        )

    def test_01_basic_containment_locks_compromised_account(self):
        """[Basic] Koan 6A: Memastikan akun terkompromi langsung diblokir (HTTP 423 Locked) untuk isolasi insiden"""
        # Akses dengan akun aman
        self.client.force_authenticate(user=self.secure_user)
        response = self.client.get('/api/resource/sensitive/')
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg="Akun yang aman diblokir secara keliru oleh sistem!"
        )

        # Akses dengan akun terkompromi via Python attribute
        self.client.force_authenticate(user=self.compromised_user)
        response = self.client.get('/api/resource/sensitive/')
        self.assertEqual(
            response.status_code,
            status.HTTP_423_LOCKED,
            msg="Akun terkompromi (Python attribute) tidak diblokir! Ini membahayakan sistem."
        )

        # Tambahkan tanda kompromi di database untuk akun secure_user
        CompromisedUser.objects.create(user_email=self.secure_user.email, is_compromised=True)
        
        # Akses kembali dengan secure_user (harus diblokir karena tercatat di database)
        self.client.force_authenticate(user=self.secure_user)
        response = self.client.get('/api/resource/sensitive/')
        self.assertEqual(
            response.status_code,
            status.HTTP_423_LOCKED,
            msg="Akun terkompromi di database tidak diblokir oleh sistem!"
        )

    def test_02_intermediate_bppa_report_structure_and_persistence(self):
        """[Intermediate] Koan 6B: Memastikan generator laporan menghasilkan data standar Pasal 35 UU PDP dan menyimpan status terkirim"""
        self.client.force_authenticate(user=self.secure_user)
        
        url = '/api/breach-report/'
        response = self.client.post(url, {
            "incident_id": self.incident.id
        }, format='json')
        
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg="Gagal memproses draf laporan insiden BPPA!"
        )
        
        data = response.data
        
        # Validasi struktur wajib Pasal 35 ayat 1
        self.assertEqual(data["incident_id"], self.incident.id)
        self.assertEqual(data["failure_cause"], self.incident.root_cause)
        self.assertEqual(data["affected_users"], self.incident.impacted_subjects_count)
        self.assertEqual(data["mitigation_actions"], self.incident.remediation_actions)
        self.assertIn("incident_time", data)
        
        # Validasi bahwa database mencatat status terlaporkan
        self.incident.refresh_from_db()
        self.assertTrue(
            self.incident.reported_to_bppa,
            msg="Status database 'reported_to_bppa' tidak berubah menjadi True setelah laporan di-generate!"
        )

    def test_03_advanced_automatic_threat_containment(self):
        """[Advanced] Koan 6C: Deteksi anomali otomatis mengunci akun pengguna di database secara instan"""
        # Login dengan user aman
        self.client.force_authenticate(user=self.secure_user)
        
        # Akses dengan parameter pemicu anomali (trigger_anomaly)
        response = self.client.get('/api/resource/sensitive/?trigger_anomaly=true')
        self.assertEqual(
            response.status_code,
            status.HTTP_423_LOCKED,
            msg="Request anomali terdeteksi seharusnya langsung ditolak dengan HTTP 423 Locked!"
        )
        
        # Pastikan user terdaftar otomatis sebagai compromised di database
        compromised_record = CompromisedUser.objects.filter(user_email=self.secure_user.email).first()
        self.assertIsNotNone(
            compromised_record,
            msg="User yang memicu anomali harus otomatis tersimpan di database CompromisedUser!"
        )
        self.assertTrue(
            compromised_record.is_compromised,
            msg="Status is_compromised di database harus True setelah dipicu anomali!"
        )
        
        # Pengguna mencoba mengakses kembali tanpa pemicu anomali (harus tetap terblokir)
        response = self.client.get('/api/resource/sensitive/')
        self.assertEqual(
            response.status_code,
            status.HTTP_423_LOCKED,
            msg="Setelah terdeteksi anomali, akses berikutnya harus tetap terkunci!"
        )
