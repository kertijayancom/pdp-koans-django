from django.test import TestCase
from django.db import connection
from koans.k03_data_security.models import CustomerRecord, ENCRYPTION_KEY
from cryptography.fernet import Fernet

class DataSecurityTestCase(TestCase):
    
    def test_01_data_is_encrypted_in_database(self):
        """Koan 3A: Memastikan NIK disimpan dalam kondisi terenkripsi di database (ciphertext)"""
        plain_nik = "3273012345678901"
        
        record = CustomerRecord.objects.create(
            name="Siti",
            nik=plain_nik
        )
        
        # Lakukan query SQL mentah bypass ORM Django untuk melihat data asli di tabel database
        with connection.cursor() as cursor:
            cursor.execute("SELECT nik FROM pdp_customer_records WHERE id = %s", [record.id])
            row = cursor.fetchone()
            db_value = row[0]
            
        self.assertNotEqual(
            db_value, 
            plain_nik,
            msg="Data NIK disimpan dalam bentuk teks biasa (plain text) di database! Ini melanggar Pasal 39 UU PDP."
        )
        
        # Memastikan data yang tersimpan bisa didekripsi dengan kunci yang benar
        try:
            fernet = Fernet(ENCRYPTION_KEY)
            decrypted = fernet.decrypt(db_value.encode('utf-8')).decode('utf-8')
            self.assertEqual(decrypted, plain_nik)
        except Exception:
            self.fail("Data yang disimpan di database tidak terenkripsi menggunakan format Fernet yang valid!")

    def test_02_data_is_decrypted_in_orm(self):
        """Koan 3B: Memastikan NIK otomatis didekripsi ketika dibaca kembali oleh aplikasi melalui ORM Django"""
        plain_nik = "3273998877665544"
        
        record = CustomerRecord.objects.create(
            name="Joko",
            nik=plain_nik
        )
        
        # Baca kembali record dari database menggunakan Django ORM
        retrieved_record = CustomerRecord.objects.get(id=record.id)
        
        self.assertEqual(
            retrieved_record.nik,
            plain_nik,
            msg="ORM gagal mendekripsi data NIK ketika dibaca kembali! Pastikan `from_db_value` telah diimplementasikan dengan benar."
        )
