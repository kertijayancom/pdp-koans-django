from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from koans.k04_rbac_audit.models import AccessAuditLog

class ExplicitRBACAuditTestCase(APITestCase):

    def setUp(self):
        # Buat user biasa (Staff / Non-DPO)
        self.non_dpo = User.objects.create_user(
            username="staff_biasa",
            email="staff@example.com",
            password="secure_password"
        )
        self.non_dpo.is_dpo = False # Bukan DPO
        
        # Buat user dengan peran DPO (Data Protection Officer)
        self.dpo = User.objects.create_user(
            username="dpo_officer",
            email="dpo@example.com",
            password="secure_password"
        )
        self.dpo.is_dpo = True # Memiliki wewenang DPO

    def test_01_non_dpo_denied_access(self):
        """Koan 4A: Memastikan user non-DPO ditolak aksesnya (HTTP 403) dan tidak mencatat log audit"""
        self.client.force_authenticate(user=self.non_dpo)
        
        url = '/api/customers/999/sensitive/'
        response = self.client.get(url)
        
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            msg="User non-DPO berhasil mengakses data sensitif! Seharusnya ditolak dengan HTTP 403 Forbidden."
        )
        
        # Memastikan tidak ada log akses yang ditulis untuk DPO abal-abal ini
        logs_count = AccessAuditLog.objects.filter(operator_email=self.non_dpo.email).count()
        self.assertEqual(
            logs_count,
            0,
            msg="User yang ditolak aksesnya secara aneh malah mencatat log audit akses!"
        )

    def test_02_dpo_allowed_and_logged(self):
        """Koan 4B: Memastikan DPO diizinkan masuk (HTTP 200) dan aktivitasnya tercatat di log audit"""
        self.client.force_authenticate(user=self.dpo)
        
        target_id = "101"
        url = f'/api/customers/{target_id}/sensitive/'
        response = self.client.get(url)
        
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg="DPO ditolak mengakses data sensitif! Seharusnya diizinkan dengan HTTP 200 OK."
        )
        
        # Memastikan log audit tersimpan dengan benar
        log = AccessAuditLog.objects.filter(
            operator_email=self.dpo.email,
            accessed_user_id=target_id,
            action="VIEW_SENSITIVE_DATA"
        ).first()
        
        self.assertIsNotNone(
            log,
            msg="Akses DPO berhasil tetapi sistem tidak mencatat log audit (AccessAuditLog) di database!"
        )
        
        self.assertEqual(
            log.action,
            "VIEW_SENSITIVE_DATA",
            msg="Aksi log audit yang dicatat tidak sesuai! Seharusnya 'VIEW_SENSITIVE_DATA'."
        )
