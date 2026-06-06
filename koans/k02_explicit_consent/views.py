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
        consent_given = request.data.get('consent_given', False)
        policy_version = request.data.get('policy_version', 'v1.0')
        
        # Mendapatkan IP Address user secara aman
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')

        # -------------------------------------------------------------------------
        # TANTANGAN KOAN 2: Validasi & Logging Explicit Consent
        # 1. Validasi jika `consent_given` bernilai False atau bukan boolean True.
        #    Jika tidak setuju, kembalikan HTTP 400 Bad Request dengan detail error.
        # 2. Jika disetujui, simpan log persetujuan ke database (ConsentLog).
        # 3. Kembalikan HTTP 201 Created dengan pesan registrasi sukses.
        # -------------------------------------------------------------------------
        
        # TODO: Tulis logika validasi dan penyimpanan log persetujuan di sini.
        # Catatan: Pastikan `ConsentLog` dibuat dengan field user_email, consent_given, 
        # ip_address, dan policy_version.

        
        # Default placeholder (saat ini meloloskan semua request tanpa log - TIDAK PATUH!)
        return Response(
            {"message": "Registration received (but consent not logged!)"},
            status=status.HTTP_200_OK
        )
