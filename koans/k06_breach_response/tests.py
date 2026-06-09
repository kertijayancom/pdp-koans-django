from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from koans.k06_breach_response.models import IncidentReport

class BreachIncidentResponseTestCase(APITestCase):

    def setUp(self):
        # User 1: Akun aman
        self.secure_user = User.objects.create_user(
            username="secure_dev",
            email="secure@example.com",
            password="password_aman"
        )
        self.secure_user.is_compromised = False
        
        # User 2: Akun terkompromi/diretas
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

    def test_01_containment_locks_compromised_account(self):
        """Koan 6A: Memastikan akun terkompromi langsung diblokir (HTTP 423 Locked) untuk isolasi insiden"""
        # Akses dengan akun aman
        self.client.force_authenticate(user=self.secure_user)
        response = self.client.get('/api/resource/sensitive/')
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg="Akun yang aman diblokir secara keliru oleh sistem!"
        )

        # Akses dengan akun terkompromi
        self.client.force_authenticate(user=self.compromised_user)
        response = self.client.get('/api/resource/sensitive/')
        self.assertEqual(
            response.status_code,
            status.HTTP_423_LOCKED,
            msg="Akun terkompromi tidak diblokir! Ini membahayakan sistem dan melanggar isolasi insiden keamanan."
        )

    def test_02_bppa_report_structure_and_persistence(self):
        """Koan 6B: Memastikan generator laporan menghasilkan data standar Pasal 35 UU PDP dan menyimpan status terkirim"""
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
