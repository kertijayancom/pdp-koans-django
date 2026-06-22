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
        # Tantangan Level Advanced: Tambahkan argumen --archive untuk mengaktifkan backup sebelum dihapus
        parser.add_argument(
            '--archive',
            action='store_true',
            default=False,
            help='Arsipkan log yang kedaluwarsa ke dalam berkas JSON sebelum dihapus'
        )
        # Tantangan Level Intermediate: Tambahkan argumen --chunk-size untuk pembatasan chunk penghapusan
        parser.add_argument(
            '--chunk-size',
            type=int,
            default=1000,
            help='Jumlah baris maksimal yang dihapus per iterasi query'
        )

    def handle(self, *args, **options):
        """
        Skenario:
        Untuk mematuhi aturan retensi data pribadi, semua record di dalam `ActionAuditLog`
        yang umurnya sudah melebihi batas hari retensi (`--days`) harus dimusnahkan.
        """
        days = options['days']
        archive = options['archive']
        chunk_size = options['chunk_size']

        # -------------------------------------------------------------------------
        # TANTANGAN KOAN 10A, 10B, 10C: Purge & Archival (Basic, Intermediate, Advanced)
        # 1. Hitung tanggal batas waktu (*threshold date*) menggunakan waktu saat ini (`timezone.now()`)
        #    dikurangi jangka waktu retensi tersebut (days).
        # 2. [Advanced] Jika `archive` bernilai True, arsipkan data log yang kedaluwarsa ke dalam file JSON
        #    di folder 'koans/k10_data_retention/archives/' sebelum dihapus fisik.
        # 3. [Intermediate] Hapus log kedaluwarsa secara bertahap menggunakan limit berukuran `chunk_size`
        #    di dalam perulangan loop agar tidak mengunci database.
        # 4. [Basic] Tulis jumlah data yang berhasil dihapus ke standard output (self.stdout.write).
        #    - Jika diarsipkan: "Archived and deleted X expired log records."
        #    - Jika tidak diarsipkan: "Deleted X expired log records."
        # -------------------------------------------------------------------------
        
        # TODO: Implementasikan logika retensi data di sini.

        # Placeholder sebelum diimplementasikan
        self.stdout.write("Command not implemented yet.")
