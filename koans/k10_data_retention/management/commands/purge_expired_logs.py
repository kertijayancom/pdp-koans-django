from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

# Impor model yang dibutuhkan
from koans.k10_data_retention.models import ActionAuditLog

class Command(BaseCommand):
    help = 'TANTANGAN KOAN 10: Kebijakan Retensi Data (Data Retention Policy - UU PDP Pasal 16 & 43)'

    def add_arguments(self, parser):
        # Menerima argumen jumlah hari retensi. Default adalah 365 hari (1 tahun) jika tidak ditentukan.
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Jumlah hari retensi data log sebelum dihapus'
        )

    def handle(self, *args, **options):
        """
        Skenario:
        Untuk mematuhi aturan retensi data pribadi, semua record di dalam `ActionAuditLog`
        yang umurnya sudah melebihi batas hari retensi (`--days`) harus dimusnahkan.
        
        Tugas Anda:
        1. Dapatkan nilai parameter `days` dari dictionary `options`.
        2. Hitung tanggal batas waktu (*threshold date*) menggunakan waktu saat ini (`timezone.now()`)
           dikurangi jangka waktu retensi tersebut (gunakan `timedelta`).
        3. Lakukan filter pada `ActionAuditLog` dan hapus (`.delete()`) semua log dengan `timestamp` yang
           lebih lama/kecil dari tanggal batas waktu tersebut.
        4. Tulis jumlah data yang berhasil dihapus ke standard output (menggunakan `self.stdout.write`)
           dengan format persis seperti ini: "Deleted X expired log records." (di mana X adalah angka count-nya).
        """
        days = options['days']
        
        # -------------------------------------------------------------------------
        # TULIS SOLUSI ANDA DI SINI
        # -------------------------------------------------------------------------

        # Placeholder sebelum diimplementasikan
        self.stdout.write("Command not implemented yet.")
