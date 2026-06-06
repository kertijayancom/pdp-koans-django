from django.db import models

class UserProfile(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField()
    
    # -------------------------------------------------------------------------
    # TANTANGAN KOAN 1A: Minimisasi Data (Pasal 16 UU PDP)
    # Hapus atau beri komentar pada field di bawah ini yang dianggap berlebihan 
    # (tidak relevan dengan fungsi inti e-commerce: transaksi & pengiriman)
    # -------------------------------------------------------------------------
    religion = models.CharField(max_length=50, blank=True, null=True)
    blood_type = models.CharField(max_length=5, blank=True, null=True)
    political_leaning = models.CharField(max_length=50, blank=True, null=True)
    
    # Field yang sah & relevan untuk operasional e-commerce
    phone_number = models.CharField(max_length=20)
    shipping_address = models.TextField()

    # -------------------------------------------------------------------------
    # TANTANGAN KOAN 1B: Masking Data Sensitif
    # Implementasikan property `masked_phone_number` di bawah ini.
    # Aturan masking: Ubah angka di tengah menjadi asterik (*), sisakan 3 angka 
    # di awal dan 4 angka di akhir. Contoh: '081234567890' -> '081****7890'
    # -------------------------------------------------------------------------
    @property
    def masked_phone_number(self):
        # TODO: Implementasikan logika masking di sini
        return self.phone_number
