from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from koans.k06_breach_response.models import IncidentReport, CompromisedUser

class SecureSensitiveResourceView(APIView):
    """
    GET /api/resource/sensitive/
    Simulasi resource sensitif yang harus langsung memblokir akses pengguna
    jika akun mereka terdeteksi dalam kondisi terkompromi/diretas (is_compromised = True).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # -------------------------------------------------------------------------
        # TANTANGAN KOAN 6C: Deteksi Anomali & Containment Otomatis (Level: Advanced)
        # Jika query parameter `trigger_anomaly` bernilai 'true', sistem secara otomatis
        # mendaftarkan email pengguna ke model `CompromisedUser` di database dengan status
        # `is_compromised = True`, lalu mengembalikan HTTP 423 Locked.
        # -------------------------------------------------------------------------
        
        # TODO: Implementasikan deteksi anomali otomatis di sini.

        # -------------------------------------------------------------------------
        # TANTANGAN KOAN 6A: Incident Containment / Lockout (Level: Basic)
        # Cek apakah akun terkompromi via Python attribute `is_compromised` atau
        # tercatat di database `CompromisedUser` dengan status compromised.
        # Jika ya, segera kembalikan status HTTP 423 Locked.
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
        # TANTANGAN KOAN 6B: BPPA Incident Report Generator (Level: Intermediate)
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
        
        # TODO: Implementasikan pencarian insiden, pembuatan laporan BPPA, dan update status di sini.

        # Placeholder output sementara (Belum sesuai standar Pasal 35!)
        return Response(
            {"message": "Incident report generator under construction"},
            status=status.HTTP_200_OK
        )
