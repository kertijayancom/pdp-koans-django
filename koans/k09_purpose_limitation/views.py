from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model

# Impor model yang dibutuhkan
from koans.k01_data_minimization.models import UserProfile
from koans.k09_purpose_limitation.models import GranularMarketingConsent
from koans.k06_breach_response.models import CompromisedUser

User = get_user_model()

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
          telah memberikan persetujuan untuk tujuan pemasaran.
        - Pengguna yang tidak aktif (is_active=False) atau akunnya terdeteksi diretas (is_compromised=True)
          harus disaring keluar demi keamanan.
        """
        category = request.data.get('category') or request.GET.get('category')
        
        # -------------------------------------------------------------------------
        # TANTANGAN KOAN 09A & 09B: Penyaringan Persetujuan Umum (Basic) & Granular (Intermediate)
        # 1. Jika `category` dikirimkan (tidak None), ambil daftar user dari database 
        #    `GranularMarketingConsent` yang menyetujui (`consent_given=True`) kategori tersebut.
        # 2. Jika `category` tidak dikirimkan, ambil daftar user dari `UserProfile` yang
        #    menyetujui pemasaran umum (`marketing_consent=True`).
        # -------------------------------------------------------------------------

        # TODO: Implementasikan penyaringan persetujuan iklan (umum / granular) di sini.

        # -------------------------------------------------------------------------
        # TANTANGAN KOAN 09C: Penyaringan Kepatuhan & Keamanan Menyeluruh (Level: Advanced)
        # Pastikan Anda menyaring keluar (exclude) semua email pengguna yang:
        # - Akunnya tidak aktif (is_active = False di django User model)
        # - Akunnya terdeteksi compromised (is_compromised = True di database CompromisedUser)
        # -------------------------------------------------------------------------

        # TODO: Tulis logika penyaringan kepatuhan menyeluruh (keaktifan & kompromi) di sini.

        # Placeholder response sebelum Anda mengimplementasikan logika di atas.
        # Anda harus mengembalikan Response dengan list email penerima yang valid.
        return Response(
            {"message": "Implement purpose limitation filtering logic here."},
            status=status.HTTP_501_NOT_IMPLEMENTED
        )
