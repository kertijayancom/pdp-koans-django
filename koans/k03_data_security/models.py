import os
from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet

# Kunci enkripsi untuk testing. Di production, simpan ini di env variable aman.
ENCRYPTION_KEY = b'p-W35x4g83b7tX_Vn6S7bY7xZ8lQ-w19aB9eC9dE9fG='

class EncryptedCharField(models.CharField):
    """
    TANTANGAN KOAN 3: Bidang Enkripsi Kustom (Encrypted Model Field)
    Implementasikan field Django kustom agar data sensitif dienkripsi secara transparan 
    sebelum masuk ke database (saat disimpan) dan didekripsi kembali saat dibaca.
    
    Petunjuk:
    1. Gunakan `Fernet(ENCRYPTION_KEY)` untuk enkripsi & dekripsi.
    2. Override method `get_prep_value(self, value)` untuk mengenkripsi data string 
       menjadi string terenkripsi (ciphertext) sebelum disimpan ke DB.
    3. Override method `from_db_value(self, value, expression, connection)` untuk 
       mendekripsi data ciphertext dari DB kembali menjadi teks asli (plaintext).
    """
    
    def get_prep_value(self, value):
        if value is None:
            return value
        # TODO: Implementasikan logika enkripsi di sini.
        # Konversi string ke bytes, enkripsi menggunakan Fernet, lalu konversi kembali ke string (utf-8).
        return value

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        # TODO: Implementasikan logika dekripsi di sini.
        # Konversi string ciphertext ke bytes, dekripsi dengan Fernet, lalu decode kembali ke string (utf-8).
        return value


class CustomerRecord(models.Model):
    name = models.CharField(max_length=100)
    
    # Field NIK ini harus terenkripsi di database menggunakan field kustom di atas
    nik = EncryptedCharField(max_length=255) 

    class Meta:
        db_table = 'pdp_customer_records'
