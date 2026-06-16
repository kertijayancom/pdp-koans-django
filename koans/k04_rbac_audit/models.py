from django.db import models

class AccessAuditLog(models.Model):
    operator_email = models.EmailField()
    action = models.CharField(max_length=100)
    accessed_user_id = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # -------------------------------------------------------------------------
    # TANTANGAN KOAN 4C & 4D: Cryptographic Hash Chain [LEVEL: ADVANCED]
    # -------------------------------------------------------------------------
    previous_hash = models.CharField(max_length=64, blank=True, null=True)
    hash_signature = models.CharField(max_length=64, blank=True, null=True)

    def calculate_hash(self):
        """
        Tugas Level Advanced:
        Hitung nilai SHA256 hash dari data record ini digabungkan dengan previous_hash.
        Gabungkan string dengan urutan:
        f"{self.operator_email}|{self.action}|{self.accessed_user_id}|{self.ip_address}|{self.previous_hash}"
        
        Kembalikan string hex dari hash tersebut (hexdigest()).
        """
        # TODO: Implementasikan fungsi penghitungan hash di sini
        return ""

    @staticmethod
    def verify_integrity():
        """
        Tugas Level Advanced:
        Verifikasi integritas seluruh rantai log audit di database dari baris pertama 
        hingga terakhir.
        Aturan verifikasi:
        1. Ambil seluruh log di database berurutan berdasarkan id.
        2. Untuk log pertama, previous_hash harus kosong/None/string kosong.
        3. Untuk log kedua dan seterusnya, previous_hash harus cocok dengan hash_signature log sebelumnya.
        4. Untuk setiap log, hitung ulang hash-nya menggunakan `calculate_hash()`, 
           dan pastikan cocok dengan nilai `hash_signature` yang tersimpan.
        
        Kembalikan True jika seluruh rantai utuh, kembalikan False jika terdeteksi manipulasi data.
        """
        # TODO: Implementasikan fungsi verifikasi rantai integritas di sini
        return True
    
    class Meta:
        db_table = 'pdp_access_audit_logs'
