from django.test import TestCase
from django.db import connection
from koans.k03_data_security.models import CustomerRecord, PRIMARY_KEY, FALLBACK_KEYS
from cryptography.fernet import Fernet

class DataSecurityTestCase(TestCase):
    
    def test_01_data_is_encrypted_in_database(self):
        """[Intermediate] Koan 3A: Memastikan NIK disimpan dalam kondisi terenkripsi di database (ciphertext) melalui Custom Field"""
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
        
        # Memastikan data yang tersimpan bisa didekripsi dengan kunci utama yang benar [Basic check]
        try:
            fernet = Fernet(PRIMARY_KEY)
            decrypted = fernet.decrypt(db_value.encode('utf-8')).decode('utf-8')
            self.assertEqual(decrypted, plain_nik)
        except Exception:
            self.fail("Data yang disimpan di database tidak terenkripsi menggunakan format Fernet yang valid dengan PRIMARY_KEY!")

    def test_02_data_is_decrypted_in_orm(self):
        """[Intermediate] Koan 3B: Memastikan NIK otomatis didekripsi ketika dibaca kembali oleh aplikasi melalui ORM Django"""
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

    def test_03_key_rotation_fallback(self):
        """[Advanced] Koan 3C: Memastikan sistem dapat mendekripsi record lama yang dienkripsi menggunakan fallback key (rotasi kunci)"""
        plain_nik = "1234567890123456"
        
        # Kita simulasikan enkripsi NIK secara manual menggunakan salah satu kunci lama (FALLBACK_KEYS)
        legacy_key = FALLBACK_KEYS[0]
        fernet = Fernet(legacy_key)
        encrypted_legacy_nik = fernet.encrypt(plain_nik.encode('utf-8')).decode('utf-8')
        
        # Simpan langsung ke database bypass ORM (agar data tersimpan dalam bentuk enkripsi kunci lama)
        # Note: CustomerRecord disave dengan NIK terenkripsi manual
        record = CustomerRecord.objects.create(
            name="Rian",
            nik=encrypted_legacy_nik
        )
        # Force update agar tidak ter-double encrypt oleh ORM jika disave
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE pdp_customer_records SET nik = %s WHERE id = %s",
                [encrypted_legacy_nik, record.id]
            )

        # Coba ambil data melalui ORM Django
        # Sistem saat ini menggunakan PRIMARY_KEY baru, namun dari_db_value harus mencoba FALLBACK_KEYS jika decryption gagal
        retrieved_record = CustomerRecord.objects.get(id=record.id)
        
        self.assertEqual(
            retrieved_record.nik,
            plain_nik,
            msg="Dekripsi gagal! Custom field harusnya mencoba mendekripsi menggunakan FALLBACK_KEYS jika kunci utama (PRIMARY_KEY) gagal (grace period rotasi kunci)."
        )
