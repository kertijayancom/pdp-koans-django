from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission
from koans.k04_rbac_audit.models import AccessAuditLog

class IsDataProtectionOfficer(BasePermission):
    """
    TANTANGAN KOAN 4A: Custom Permission DRF (RBAC - Pasal 40 UU PDP)
    Implementasikan izin akses kustom agar hanya user DPO yang dapat mengakses.
    
    Kriteria:
    - User harus sudah terautentikasi (`request.user.is_authenticated`).
    - User harus memiliki flag `is_dpo` bernilai True (gunakan `getattr(request.user, 'is_dpo', False)`).
    """
    def has_permission(self, request, view):
        # TODO: Kembalikan True jika user terautentikasi dan merupakan DPO.
        # Saat ini default-nya True (TIDAK AMAN! Semua orang bisa akses!)
        return True


class CustomerSensitiveDataView(APIView):
    """
    GET /api/customers/<id>/sensitive/
    Melihat data sensitif pelanggan. Wajib dilindungi dengan permission kustom 
    dan mencatat log audit akses (Access Audit Trail - ISO 27001 Control A.8.2).
    """
    # Pasang custom permission class yang sudah dibuat di atas
    permission_classes = [IsDataProtectionOfficer]

    def get(self, request, id, *args, **kwargs):
        # Mendapatkan IP Address operator secara aman
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')

        # -------------------------------------------------------------------------
        # TANTANGAN KOAN 4: Access Audit Trail & Cryptographic Chain
        #
        # [LEVEL 1: BASIC] - Custom Permission Class
        # 1. Pastikan endpoint dilindungi dengan kelas izin `IsDataProtectionOfficer` di atas.
        #
        # [LEVEL 2: INTERMEDIATE] - Perekaman Log Akses Dasar
        # 2. Simpan catatan akses ke model `AccessAuditLog` dengan field:
        #    - `operator_email`: email dari user yang sedang login (`request.user.email`).
        #    - `action`: "VIEW_SENSITIVE_DATA"
        #    - `accessed_user_id`: ID pelanggan yang datanya diakses (`id`).
        #    - `ip_address`: IP Address pemohon (`ip`).
        #
        # [LEVEL 3: ADVANCED] - Cryptographic Hash Chain (Tamper-Resistant Audit Log)
        # 3. Sebelum menyimpan log baru, cari record log terakhir yang tersimpan di database.
        #    - Jika log terakhir ada, set `previous_hash` log baru dengan `hash_signature` dari log terakhir tersebut.
        #    - Jika database log masih kosong, set `previous_hash = ""` (string kosong).
        # 4. Hitung nilai signature untuk log baru ini menggunakan method `.calculate_hash()`.
        # 5. Simpan nilai hasil kalkulasi tersebut ke dalam field `hash_signature`.
        # -------------------------------------------------------------------------
        
        # TODO: Simpan log audit akses dengan hash signature di sini sebelum mengembalikan respons.

        # Data sensitif tiruan yang dikembalikan
        mock_data = {
            "customer_id": id,
            "nik": "3273012345678901",
            "monthly_income": 25000000,
            "medical_history": "Hipertensi tingkat 1"
        }
        
        return Response(mock_data, status=status.HTTP_200_OK)
