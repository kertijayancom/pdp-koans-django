from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import connection
from koans.k01_data_minimization.models import UserProfile

User = get_user_model()

class DataMinimizationTestCase(TestCase):
    
    def test_01_excessive_fields_removed(self):
        """[Advanced] Koan 1A: Memastikan field berlebih (religion, blood_type, political_leaning) telah dihapus dari kode Model"""
        fields = [f.name for f in UserProfile._meta.get_fields()]
        
        excessive_fields = ['religion', 'blood_type', 'political_leaning']
        for field in excessive_fields:
            self.assertNotIn(
                field, 
                fields, 
                msg=f"Field '{field}' melanggar prinsip minimisasi data (Pasal 16 UU PDP). Harap hapus field ini dari model!"
            )

    def test_02_phone_number_masked_correctly(self):
        """[Basic] Koan 1B: Memastikan no telepon disamarkan dengan aman di property basic"""
        profile = UserProfile(
            username="budi",
            email="budi@example.com",
            phone_number="081234567890",
            shipping_address="Jakarta"
        )
        
        # Check standard masking
        self.assertEqual(
            profile.masked_phone_number, 
            "081****7890", 
            msg="Format masking nomor telepon tidak sesuai! Harap ubah bagian tengah nomor menjadi asterik (*) dan sisakan 3 angka awal serta 4 angka akhir."
        )

        # Check safety check if short phone number is passed
        profile.phone_number = "12345"
        self.assertNotEqual(
            profile.masked_phone_number,
            "12345",
            msg="Harap pastikan nomor telepon yang pendek juga di-mask atau tidak langsung dibocorkan mentah-mentah!"
        )

    def test_03_context_aware_masking(self):
        """[Intermediate] Koan 1C: Memastikan masking nomor telepon dinamis (context-aware) berdasarkan peran pengakses"""
        profile = UserProfile(
            username="budi",
            email="budi@example.com",
            phone_number="081234567890",
            shipping_address="Jakarta"
        )

        # 1. Regular User (Harus melihat nomor yang di-masking)
        regular_user = User(username="regular", email="reg@pdp.local", is_staff=False)
        self.assertEqual(
            profile.get_masked_phone_number(regular_user),
            "081****7890",
            msg="User biasa harusnya hanya bisa melihat nomor telepon yang sudah disamarkan!"
        )

        # 2. Staff User (Harus melihat nomor telepon asli)
        staff_user = User(username="staff", email="staff@pdp.local", is_staff=True)
        self.assertEqual(
            profile.get_masked_phone_number(staff_user),
            "081234567890",
            msg="Staf operasional harus bisa melihat nomor telepon asli untuk pemrosesan!"
        )

        # 3. DPO User (Harus melihat nomor telepon asli)
        dpo_user = User(username="dpo", email="dpo@pdp.local", is_staff=False)
        dpo_user.is_dpo = True  # Mock attribute DPO
        self.assertEqual(
            profile.get_masked_phone_number(dpo_user),
            "081234567890",
            msg="Data Protection Officer (DPO) harus memiliki wewenang membaca data asli untuk audit!"
        )

    def test_04_database_dropped_columns(self):
        """[Advanced] Koan 1D: Memastikan kolom berlebih benar-benar telah di-drop dari skema tabel database fisik"""
        db_table = UserProfile._meta.db_table
        
        with connection.cursor() as cursor:
            # Menggunakan raw SQL query untuk mengambil metadata kolom tabel fisik
            # Kompatibel untuk SQLite (testing default) maupun PostgreSQL (production)
            cursor.execute(f"SELECT * FROM {db_table} LIMIT 1")
            col_names = [desc[0] for desc in cursor.description]
        
        excessive_columns = ['religion', 'blood_type', 'political_leaning']
        for col in excessive_columns:
            self.assertNotIn(
                col,
                col_names,
                msg=f"Kolom fisik '{col}' masih bersarang di database Anda! Anda wajib menjalankan 'python manage.py makemigrations' dan 'python manage.py migrate' untuk menghapusnya secara fisik."
            )
