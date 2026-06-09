from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser

# Impor model yang dibutuhkan
from koans.k01_data_minimization.models import UserProfile

class MarketingDispatchView(APIView):
    # Mengamankan endpoint agar hanya admin/staf marketing yang bisa mengakses
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        """
        TANTANGAN KOAN 09: Pembatasan Tujuan (Purpose Limitation - UU PDP Pasal 16 & 27)
        
        Skenario:
        Departemen pemasaran ingin mengirimkan newsletter promo (konten marketing) ke semua pengguna.
        Namun, berdasarkan asas Pembatasan Tujuan (Purpose Limitation) pada UU PDP:
        - Kita hanya boleh mengirimkan komunikasi pemasaran kepada pengguna yang secara eksplisit
          telah memberikan persetujuan untuk tujuan pemasaran (`marketing_consent = True`).
        - Pengguna yang tidak memberikan persetujuan pemasaran (`marketing_consent = False`) harus
          disaring keluar, meskipun akun mereka dalam keadaan aktif dan terdaftar untuk transaksi.
          
        Tugas Anda:
        1. Ambil daftar semua `UserProfile` dari database.
        2. Saring (filter) profil tersebut sehingga hanya menghasilkan user yang memiliki `marketing_consent = True`.
        3. Kembalikan list email dari pengguna yang lolos filter dalam response JSON:
           `{"recipients": ["user1@email.com", "user2@email.com"]}`.
        """
        
        # -------------------------------------------------------------------------
        # TULIS SOLUSI ANDA DI SINI
        # -------------------------------------------------------------------------
        
        # Placeholder response sebelum Anda mengimplementasikan logika di atas.
        # Anda harus mengembalikan Response dengan list email penerima yang valid.
        return Response(
            {"message": "Implement purpose limitation filtering logic here."},
            status=status.HTTP_501_NOT_IMPLEMENTED
        )
