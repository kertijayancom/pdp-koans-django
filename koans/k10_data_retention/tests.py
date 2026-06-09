from django.test import TestCase
from django.utils import timezone
from django.core.management import call_command
from io import StringIO
from datetime import timedelta

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

    def test_purge_expired_logs_command(self):
        """Koan 10: Running purge command deletes only expired logs and outputs details"""
        out = StringIO()
        
        # Jalankan management command dengan parameter days=30
        call_command('purge_expired_logs', days=30, stdout=out)
        
        # Ambil output teks dari console
        command_output = out.getvalue().strip()
        
        # Verifikasi log lama terhapus (hanya menyisakan new_log dan mid_log)
        self.assertEqual(ActionAuditLog.objects.count(), 2)
        
        self.assertTrue(ActionAuditLog.objects.filter(id=self.new_log.id).exists())
        self.assertTrue(ActionAuditLog.objects.filter(id=self.mid_log.id).exists())
        
        self.assertFalse(ActionAuditLog.objects.filter(id=self.old_log1.id).exists())
        self.assertFalse(ActionAuditLog.objects.filter(id=self.old_log2.id).exists())
        
        # Verifikasi output stdout sesuai format
        self.assertIn("Deleted 2 expired log records.", command_output)
