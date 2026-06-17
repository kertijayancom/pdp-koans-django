from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# Impor model terkait dari koan sebelumnya untuk agregasi data
from koans.k01_data_minimization.models import UserProfile
from koans.k02_explicit_consent.models import ConsentLog
from koans.k05_data_portability.models import UserTransaction, DataExportJob

class DataPortabilityExportView(APIView):
    """
    GET /api/users/export-data/
    Mengekspor semua data pribadi milik pengguna yang sedang login
    dalam format JSON berstandar mesin (UU PDP Pasal 7 & 13).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Email pengguna yang sedang login
        user_email = request.user.email

        # -------------------------------------------------------------------------
        # TANTANGAN KOAN 5A: Pencegahan IDOR / BOLA (Level: Basic)
        # 1. Pastikan sistem mengabaikan email eksternal jika dikirim lewat query parameter
        #    (misalnya: GET /api/users/export-data/?email=korban@example.com).
        #    Sistem harus SELALU mengunci data hanya untuk `request.user.email`.
        # 2. Jika email di query parameter dikirimkan dan berbeda dengan email user login,
        #    kembalikan HTTP 403 Forbidden dengan pesan error yang jelas.
        # -------------------------------------------------------------------------
        query_email = request.GET.get('email')
        
        # TODO: Implementasikan validasi pencegahan IDOR di sini.

        # -------------------------------------------------------------------------
        # TANTANGAN KOAN 5C/5D: Polling Asynchronous Export (Level: Advanced)
        # 1. Periksa apakah parameter `job_id` ada dalam query string. Jika ya:
        #    - Cari DataExportJob yang sesuai dengan `id=job_id` dan milik pengguna login.
        #    - Jika ditemukan, ubah statusnya menjadi 'COMPLETED', isi `download_url` 
        #      dengan link mock (misal: http://localhost:8000/media/exports/export_<job_id>.json),
        #      kemudian simpan dan kembalikan dengan status HTTP 200 OK.
        #    - Jika tidak ditemukan, kembalikan HTTP 404 Not Found.
        # 2. Periksa apakah parameter `async` bernilai 'true'. Jika ya:
        #    - Buat data `DataExportJob` baru dengan status 'PENDING'.
        #    - Kembalikan respons berupa job_id dan status dengan HTTP 202 Accepted.
        # -------------------------------------------------------------------------
        job_id = request.GET.get('job_id')
        is_async = request.GET.get('async')

        # TODO: Implementasikan penanganan ekspor asinkronous (trigger & polling) di sini.

        # -------------------------------------------------------------------------
        # TANTANGAN KOAN 5B: Agregasi Data Lintas Tabel & Standardisasi JSON (Level: Intermediate)
        # Kumpulkan semua data terkait email pengguna dari tabel-tabel berikut:
        # 1. UserProfile (Koan 1) -> Ambil data profile (username, phone_number, shipping_address).
        # 2. ConsentLog (Koan 2) -> Ambil riwayat consent (timestamp, consent_given, policy_version).
        # 3. UserTransaction (Koan 5) -> Ambil semua riwayat belanja (item_name, amount, timestamp).
        # -------------------------------------------------------------------------

        # TODO: Lakukan query dan bangun struktur JSON yang rapi.
        # Tentukan default data kosong jika profile atau data lainnya tidak ditemukan.

        # Placeholder output sementara (Tidak lengkap dan belum aman!)
        export_data = {
            "exported_at": "2026-06-09T00:00:00Z",
            "message": "Data portability under construction (placeholder response)"
        }

        return Response(export_data, status=status.HTTP_200_OK)
