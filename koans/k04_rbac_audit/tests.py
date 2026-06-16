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
        """[Basic] Koan 4A: Memastikan user non-DPO ditolak aksesnya (HTTP 403) dan tidak mencatat log audit"""
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
        """[Intermediate] Koan 4B: Memastikan DPO diizinkan masuk (HTTP 200) dan aktivitasnya tercatat di log audit"""
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

    def test_03_audit_log_hash_chain_integrity(self):
        """[Advanced] Koan 4C: Memastikan log audit akses tersusun dalam Cryptographic Hash Chain yang valid"""
        self.client.force_authenticate(user=self.dpo)
        
        # 1. Trigger beberapa akses berturut-turut untuk membangun rantai log
        self.client.get('/api/customers/101/sensitive/')
        self.client.get('/api/customers/102/sensitive/')
        self.client.get('/api/customers/103/sensitive/')
        
        logs = list(AccessAuditLog.objects.all().order_by('id'))
        self.assertEqual(len(logs), 3)

        # 2. Verifikasi Log Pertama (previous_hash harus kosong/None/string kosong)
        self.assertTrue(logs[0].previous_hash == "" or logs[0].previous_hash is None)
        self.assertIsNotNone(logs[0].hash_signature)
        self.assertEqual(logs[0].hash_signature, logs[0].calculate_hash())

        # 3. Verifikasi Log Kedua dan Ketiga (previous_hash harus cocok dengan hash_signature sebelumnya)
        for i in range(1, len(logs)):
            self.assertEqual(
                logs[i].previous_hash,
                logs[i-1].hash_signature,
                msg=f"Rantai hash terputus pada log index ke-{i}! previous_hash tidak cocok dengan signature log sebelumnya."
            )
            self.assertEqual(
                logs[i].hash_signature,
                logs[i].calculate_hash(),
                msg=f"Signature kalkulasi ulang untuk log index ke-{i} tidak cocok dengan signature yang disimpan!"
            )

        # 4. Panggil fungsi verifikasi integritas global staticmethod
        self.assertTrue(
            AccessAuditLog.verify_integrity(),
            msg="Metode verify_integrity() mengembalikan False pada rantai log yang valid!"
        )

    def test_04_audit_log_tamper_detection(self):
        """[Advanced] Koan 4D: Memastikan fungsi verifikasi mendeteksi manipulasi data (data tampering) pada rantai log"""
        self.client.force_authenticate(user=self.dpo)
        
        # 1. Trigger beberapa akses
        self.client.get('/api/customers/101/sensitive/')
        self.client.get('/api/customers/102/sensitive/')
        self.client.get('/api/customers/103/sensitive/')
        
        self.assertTrue(AccessAuditLog.verify_integrity())

        # 2. Skenario Serangan A: Mengubah isi data di tengah rantai secara ilegal
        compromised_log = AccessAuditLog.objects.all().order_by('id')[1]
        compromised_log.ip_address = "9.9.9.9"  # Ubah IP address asal secara manual
        compromised_log.save()

        # Verifikasi integritas harus mengembalikan False (mendeteksi manipulasi data)
        self.assertFalse(
            AccessAuditLog.verify_integrity(),
            msg="Sistem gagal mendeteksi serangan manipulasi data (data tampering) di tengah log!"
        )

        # Kembalikan ke normal untuk test berikutnya
        compromised_log.ip_address = "127.0.0.1"
        compromised_log.save()
        self.assertTrue(AccessAuditLog.verify_integrity())

        # 3. Skenario Serangan B: Menghapus baris log di tengah rantai secara ilegal
        #    Menghapus log index ke-1 membuat previous_hash index ke-2 tidak lagi menunjuk ke siapa pun yang valid
        AccessAuditLog.objects.all().order_by('id')[1].delete()

        # Verifikasi integritas harus mengembalikan False (mendeteksi rantai patah / broken chain)
        self.assertFalse(
            AccessAuditLog.verify_integrity(),
            msg="Sistem gagal mendeteksi serangan penghapusan baris log (broken chain)!"
        )
