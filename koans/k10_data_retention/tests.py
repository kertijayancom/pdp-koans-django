from django.test import TestCase
from django.utils import timezone
from django.core.management import call_command
from io import StringIO
from datetime import timedelta
import os
import glob
import json

from koans.k10_data_retention.models import ActionAuditLog

class DataRetentionTestCase(TestCase):
    def setUp(self):
        self.now = timezone.now()
        
        # 1. Log baru (baru saja dibuat) - Tetap Harus Ada
        self.new_log = ActionAuditLog.objects.create(
            operator_email="admin@pdp.local",
            action_details="Login success",
            timestamp=self.now
        )
        
        # 2. Log berusia 15 hari - Tetap Harus Ada untuk retensi 30 hari
        self.mid_log = ActionAuditLog.objects.create(
            operator_email="admin@pdp.local",
            action_details="View sensitive customer data",
            timestamp=self.now - timedelta(days=15)
        )
        
        # 3. Log berusia 45 hari - Harus Terhapus untuk retensi 30 hari
        self.old_log1 = ActionAuditLog.objects.create(
            operator_email="admin@pdp.local",
            action_details="Export all users data",
            timestamp=self.now - timedelta(days=45)
        )

        # 4. Log berusia 60 hari - Harus Terhapus untuk retensi 30 hari
        self.old_log2 = ActionAuditLog.objects.create(
            operator_email="admin@pdp.local",
            action_details="Delete database backups",
            timestamp=self.now - timedelta(days=60)
        )

    def test_01_basic_purge_expired_logs(self):
        """[Basic] Koan 10A: Running purge command deletes only expired logs and outputs details"""
        out = StringIO()
        
        # Jalankan management command dengan parameter days=30
        call_command('purge_expired_logs', days=30, stdout=out)
        command_output = out.getvalue().strip()
        
        # Verifikasi log lama terhapus (hanya menyisakan new_log dan mid_log)
        self.assertEqual(ActionAuditLog.objects.count(), 2)
        
        self.assertTrue(ActionAuditLog.objects.filter(id=self.new_log.id).exists())
        self.assertTrue(ActionAuditLog.objects.filter(id=self.mid_log.id).exists())
        
        self.assertFalse(ActionAuditLog.objects.filter(id=self.old_log1.id).exists())
        self.assertFalse(ActionAuditLog.objects.filter(id=self.old_log2.id).exists())
        
        # Verifikasi output stdout sesuai format
        self.assertIn("Deleted 2 expired log records.", command_output)

    def test_02_intermediate_chunked_deletion(self):
        """[Intermediate] Koan 10B: Running purge command with small chunk_size loops and purges successfully"""
        out = StringIO()
        
        # Jalankan dengan chunk_size=1 (memaksa iterasi loop 2 kali)
        call_command('purge_expired_logs', days=30, chunk_size=1, stdout=out)
        command_output = out.getvalue().strip()
        
        self.assertEqual(ActionAuditLog.objects.count(), 2)
        self.assertFalse(ActionAuditLog.objects.filter(id=self.old_log1.id).exists())
        self.assertFalse(ActionAuditLog.objects.filter(id=self.old_log2.id).exists())
        self.assertIn("Deleted 2 expired log records.", command_output)

    def test_03_advanced_archival_before_deletion(self):
        """[Advanced] Koan 10C: Running command with --archive saves expired logs into JSON file before physical deletion"""
        out = StringIO()
        
        # Jalankan dengan parameter --archive aktif
        call_command('purge_expired_logs', days=30, archive=True, stdout=out)
        command_output = out.getvalue().strip()
        
        self.assertEqual(ActionAuditLog.objects.count(), 2)
        self.assertIn("Archived and deleted 2 expired log records.", command_output)
        
        # Pastikan berkas JSON terbuat di folder archives
        archive_dir = os.path.join(os.path.dirname(__file__), 'archives')
        json_files = glob.glob(os.path.join(archive_dir, 'archive_expired_logs_*.json'))
        
        self.assertTrue(len(json_files) >= 1, msg="Berkas arsip JSON tidak ditemukan di folder archives!")
        
        # Ambil berkas terbaru dan baca isinya
        latest_file = max(json_files, key=os.path.getctime)
        with open(latest_file, 'r') as f:
            archive_data = json.load(f)
            
        # Harus mengarsipkan 2 log yang dihapus
        self.assertEqual(len(archive_data), 2)
        emails = [item["operator_email"] for item in archive_data]
        self.assertEqual(emails, ["admin@pdp.local", "admin@pdp.local"])
        
        # Bersihkan berkas setelah pengujian selesai
        for f in json_files:
            try:
                os.remove(f)
            except OSError:
                pass
