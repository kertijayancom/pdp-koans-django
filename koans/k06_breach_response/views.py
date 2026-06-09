from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from koans.k06_breach_response.models import IncidentReport

class SecureSensitiveResourceView(APIView):
    """
    GET /api/resource/sensitive/
    Simulasi resource sensitif yang harus langsung memblokir akses pengguna
    jika akun mereka terdeteksi dalam kondisi terkompromi/diretas (is_compromised = True).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # -------------------------------------------------------------------------
        # TANTANGAN KOAN 6A: Incident Containment (Auto Account Lockout)
        # Jika akun terindikasi retak (periksa wewenang `getattr(request.user, 'is_compromised', False)`),
        # segera tolak akses dan kembalikan status HTTP 423 Locked untuk mengisolasi kebocoran.
        # -------------------------------------------------------------------------
        
        # TODO: Tulis logika isolasi akun di sini.
        
        return Response({"data": "Sangat Rahasia!"}, status=status.HTTP_200_OK)


class BreachNotificationReportView(APIView):
    """
    POST /api/breach-report/
    Menghasilkan draf laporan insiden kebocoran data untuk dikirim ke BPPA
    berdasarkan Pasal 35 ayat (1) UU PDP, dan menandai status terlaporkan.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        incident_id = request.data.get('incident_id')
        
        # -------------------------------------------------------------------------
        # TANTANGAN KOAN 6B: BPPA Incident Report Generator (Pasal 35)
        # 1. Cari `IncidentReport` berdasarkan `incident_id`. Jika tidak ketemu,
        #    kembalikan HTTP 404 Not Found.
        # 2. Susun data respons dengan skema JSON yang wajib dilaporkan sesuai Pasal 35 UU PDP:
        #    - `incident_id`: id insiden
        #    - `incident_time`: waktu kejadian (`timestamp.isoformat()`)
        #    - `failure_cause`: penjelasan penyebab kebocoran (`root_cause`)
        #    - `affected_users`: jumlah pengguna terdampak (`impacted_subjects_count`)
        #    - `mitigation_actions`: tindakan penanganan yang telah berjalan (`remediation_actions`)
        # 3. Ubah status model `reported_to_bppa` menjadi True dan simpan ke DB.
        # 4. Kembalikan respons terstruktur tersebut dengan status HTTP 200 OK.
        # -------------------------------------------------------------------------
        
        # TODO: Implementasikan pencarian insiden, pembuatan laporan BPPA, dan update status.

        # Placeholder output sementara (Belum sesuai standar Pasal 35!)
        return Response(
            {"message": "Incident report generator under construction"},
            status=status.HTTP_200_OK
        )
