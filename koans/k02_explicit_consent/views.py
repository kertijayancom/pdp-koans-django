from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from koans.k02_explicit_consent.models import ConsentLog

class RegisterWithConsentView(APIView):
    """
    POST /api/register/
    Mendaftarkan user baru dengan memvalidasi dan mencatat persetujuan (consent)
    sesuai UU PDP Pasal 20 & 21.
    """
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        consent_service = request.data.get('consent_service', False)
        consent_marketing = request.data.get('consent_marketing', False)
        policy_version = request.data.get('policy_version', 'v1.0')
        
        # Mendapatkan IP Address user secara aman
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')

        # -------------------------------------------------------------------------
        # TANTANGAN KOAN 2: Validasi & Logging Explicit Consent
        #
        # [LEVEL 1: BASIC] - Validasi Consent Layanan Utama
        # 1. Cek parameter `consent_service`. Jika False, batalkan registrasi dan
        #    kembalikan HTTP 400 Bad Request dengan detail error.
        #
        # [LEVEL 2: INTERMEDIATE] - Pencatatan Audit Trail
        # 2. Jika `consent_service` disetujui, simpan log bukti persetujuan ke database
        #    (buat instance `ConsentLog` baru dengan data email, ip_address, dll).
        #
        # [LEVEL 3: ADVANCED] - Anti-Bundling Consent (UU PDP Pasal 20 / RPP Pasal 55)
        # 3. Registrasi tidak boleh dibatalkan meskipun user menolak persetujuan marketing
        #    (`consent_marketing` bernilai False).
        # 4. Buat profile `UserProfile` (impor dari k01) dengan flag `marketing_consent` 
        #    yang disesuaikan dengan input `consent_marketing` (True atau False).
        # 5. Kembalikan response sukses registrasi dengan HTTP 201 Created.
        # -------------------------------------------------------------------------
        
        # TODO: Tulis logika validasi, penyimpanan log persetujuan, dan profile creation di sini.

        # Default placeholder (saat ini meloloskan semua request tanpa log - TIDAK PATUH!)
        return Response(
            {"message": "Registration received (but consent not logged!)"},
            status=status.HTTP_200_OK
        )
