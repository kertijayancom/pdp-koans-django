from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

# Impor model yang dibutuhkan
from django.contrib.auth import get_user_model
from koans.k02_explicit_consent.models import ConsentLog
from koans.k08_consent_withdrawal.models import RevokedToken

User = get_user_model()

class ConsentWithdrawalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        TANTANGAN KOAN 08: Penarikan Persetujuan (Consent Withdrawal - UU PDP Pasal 15 & 40)
        
        Skenario:
        Ketika seorang pengguna terautentikasi mengirim permintaan untuk menarik persetujuannya:
        1. Catat penarikan persetujuan di tabel ConsentLog untuk email pengguna tersebut:
           - Buat baris baru di tabel `ConsentLog` dengan status `consent_given = False`
             sebagai bukti audit log penarikan persetujuan.
           - Log tersebut harus menyertakan IP address dari request dan policy_version saat ini.
        2. Batasi pemrosesan data pribadi aktif secara langsung:
           - Ubah status `is_active` pada model User (auth.User) menjadi `False` untuk
             menolak akses login/autentikasi berikutnya ke aplikasi.
           - Jangan hapus data secara permanen, karena data historis (seperti transaksi) masih
             harus disimpan selama masa retensi hukum yang sah (misal: perpajakan).
        """
        user = request.user
        email = user.email
        ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')
        policy_version = request.data.get('policy_version', 'v1.0')
        token_jti = request.data.get('token_jti')
        
        # -------------------------------------------------------------------------
        # TANTANGAN KOAN 08A & 08B: Deactivation (Basic) & Atomic Logging (Intermediate)
        # Lakukan pencatatan penarikan persetujuan di database dan deaktifkan user secara atomik.
        # Gunakan database transaction block (`transaction.atomic`) untuk memastikan konsistensi.
        # -------------------------------------------------------------------------

        # TODO: Implementasikan pencatatan log withdrawal dan deaktifkan akun di sini.

        # -------------------------------------------------------------------------
        # TANTANGAN KOAN 08C: Blacklist Sesi Aktif / Token (Level: Advanced)
        # Jika token_jti disertakan di payload request, simpan ke database pdp_revoked_tokens
        # agar semua sesi login aktif langsung dibatalkan secara instan.
        # -------------------------------------------------------------------------

        # TODO: Implementasikan penyimpanan token pencabutan sesi di sini.

        # Placeholder response sebelum Anda mengimplementasikan logika di atas.
        # Anda harus mengembalikan Response dengan status HTTP_200_OK jika berhasil.
        return Response(
            {"message": "Implement consent withdrawal flow here."},
            status=status.HTTP_501_NOT_IMPLEMENTED
        )
