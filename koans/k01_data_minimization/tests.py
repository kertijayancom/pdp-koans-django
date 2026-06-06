from django.test import TestCase
from koans.k01_data_minimization.models import UserProfile

class DataMinimizationTestCase(TestCase):
    
    def test_01_excessive_fields_removed(self):
        """Koan 1A: Memastikan field berlebih (religion, blood_type, political_leaning) telah dihapus"""
        fields = [f.name for f in UserProfile._meta.get_fields()]
        
        excessive_fields = ['religion', 'blood_type', 'political_leaning']
        print(fields)
        for field in excessive_fields:
            self.assertNotIn(
                field, 
                fields, 
                msg=f"Field '{field}' melanggar prinsip minimisasi data (Pasal 16 UU PDP). Harap hapus field ini dari model!"
            )

    def test_02_phone_number_masked_correctly(self):
        """Koan 1B: Memastikan no telepon disamarkan dengan aman di view/log"""
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
