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
        # TANTANGAN KOAN 4B: Access Audit Trail Logging (ISO 27001 Control A.8.2)
        # 1. Simpan catatan akses ke model `AccessAuditLog`.
        #    - `operator_email`: email dari user yang sedang login (`request.user.email`).
        #    - `action`: "VIEW_SENSITIVE_DATA"
        #    - `accessed_user_id`: ID pelanggan yang datanya sedang diakses (diambil dari parameter `id`).
        #    - `ip_address`: IP Address pemohon (`ip`).
        # 2. Kembalikan data sensitif simulasi dengan HTTP 200 OK.
        # -------------------------------------------------------------------------
        
        # TODO: Simpan log audit akses ke database di sini sebelum mengembalikan respons.

        # Data sensitif tiruan yang dikembalikan
        mock_data = {
            "customer_id": id,
            "nik": "3273012345678901",
            "monthly_income": 25000000,
            "medical_history": "Hipertensi tingkat 1"
        }
        
        return Response(mock_data, status=status.HTTP_200_OK)
