import os
from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet
# Kunci enkripsi utama (Primary Key) untuk testing.
PRIMARY_KEY = b'p-W35x4g83b7tX_Vn6S7bY7xZ8lQ-w19aB9eC9dE9fG='

# Kunci enkripsi cadangan/lama (Fallback Keys) untuk simulasi rotasi kunci.
# Harus berupa 32-byte base64-encoded bytes yang valid.
FALLBACK_KEYS = [
    b'old_key_rot_1234567890123456789012345678901=',
    b'legacy_key_rot_abcdefghijklmnopqrstuvwxyz0='
]


class EncryptedCharField(models.CharField):
    """
    TANTANGAN KOAN 3: Bidang Enkripsi Kustom & Rotasi Kunci (Encrypted Model Field & Key Rotation)
    
    [LEVEL 1: BASIC] - Algoritma Enkripsi Dasar
    - Pastikan enkripsi menggunakan `cryptography.fernet.Fernet`.
    
    [LEVEL 2: INTERMEDIATE] - Custom Model Field Django ORM
    - Override method `get_prep_value(self, value)` untuk mengenkripsi data sebelum disimpan ke DB.
    - Override method `from_db_value(self, value, expression, connection)` untuk mendekripsi data dari DB.
    
    [LEVEL 3: ADVANCED] - Rotasi Kunci Enkripsi (ISO 27001 Control A.8.24)
    - Di `from_db_value`, lakukan percobaan dekripsi menggunakan `PRIMARY_KEY` terlebih dahulu.
    - Jika terjadi error (misalnya `InvalidToken` karena dienkripsi dengan kunci lama), 
      lakukan perulangan (loop) untuk mencoba mendekripsi menggunakan daftar kunci di `FALLBACK_KEYS`.
    - Jika semua kunci gagal, biarkan error terlempar.
    """
    
    def get_prep_value(self, value):
        if value is None:
            return value
        # TODO: Implementasikan logika enkripsi di sini menggunakan PRIMARY_KEY.
        return value

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        # TODO: Implementasikan logika dekripsi dengan mekanisme fallback (Multi-Key Decryption) di sini.
        return value


class CustomerRecord(models.Model):
    name = models.CharField(max_length=100)
    
    # Field NIK ini harus terenkripsi di database menggunakan field kustom di atas
    nik = EncryptedCharField(max_length=255) 

    class Meta:
        db_table = 'pdp_customer_records'
