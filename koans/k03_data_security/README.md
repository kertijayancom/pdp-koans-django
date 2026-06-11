# Learning Notes: Koan 03 - Data Security & Encryption 🛡️

Tantangan ini berfokus pada prinsip **Keamanan Data & Kriptografi (Encryption At-Rest)** berdasarkan standar ISO 27001 dan regulasi UU PDP.

---

## 1. Penjelasan Konsep (Concept Explanation)

**Encryption At-Rest** adalah proses menyandikan (mengenkripsi) data sensitif saat data tersebut disimpan di media penyimpanan fisik (seperti PostgreSQL atau SSD server), sehingga data tidak dapat dibaca tanpa kunci dekripsi yang sah.

Dalam tantangan ini:
- Kita mengamankan Nomor Induk Kependudukan (NIK) pelanggan. NIK adalah data pribadi spesifik yang memiliki risiko tinggi jika bocor.
- Kita menggunakan **Kriptografi Simetris** dengan algoritma **AES** via pustaka **Fernet** (dari modul `cryptography`). Pustaka Fernet menjamin bahwa data yang dienkripsi tidak dapat dimanipulasi atau dibaca tanpa kunci enkripsi yang tepat (*symmetric encryption key*).

Implementasinya dilakukan di tingkat ORM Django dengan membuat bidang kustom (**Custom Model Field**):
- **`get_prep_value`**: Dipicu otomatis saat data akan disimpan ke database. Kita mengubah teks biasa (plain text NIK) menjadi ciphertext terenkripsi.
- **`from_db_value`**: Dipicu otomatis saat data dibaca dari database lewat ORM. Kita mengubah ciphertext kembali menjadi teks biasa (plain text NIK).

---

## 2. Kenapa Penting (Why It Matters)

Enkripsi data sensitif di tingkat penyimpanan fisik sangat penting karena:
1. **Dampak Hukum (UU PDP Pasal 39)**: Pengendali data pribadi wajib menjaga keamanan data dari akses yang tidak sah. Menyimpan data sensitif seperti NIK atau nomor kartu kredit dalam bentuk teks biasa (*plain text*) di database adalah bentuk kelalaian hukum yang berat.
2. **Kepatuhan ISO 27001 (Control A.8.24 - Use of Cryptography)**: Standar keamanan informasi mensyaratkan penggunaan kriptografi untuk melindungi kerahasiaan, integritas, dan ketersediaan data sensitif.
3. **Mitigasi Kebocoran Cadangan Database (Database Dump Leak)**: Jika database Anda diretas atau berkas cadangan database (*database backup dump*) dicuri oleh penyerang, mereka tetap tidak dapat menyalahgunakan NIK pelanggan karena isinya hanyalah string acak terenkripsi yang tidak terbaca tanpa kunci dekripsi yang disimpan terpisah di *environment variables*.

---

## 3. Apa yang Test-nya Ajarkan (What the Test Teaches)

Unit test pada Koan 03 menguji integritas dari implementasi enkripsi kita:
1. **Transparansi ORM (`test_nik_encryption_at_rest_and_decryption`)**:
   - Memastikan bahwa saat kita mengambil data dari model Django, NIK yang didekripsi keluar dalam bentuk teks biasa yang benar. Pengguna akhir/aplikasi tidak perlu mendekripsinya secara manual.
2. **Enkripsi Fisik Database (`test_database_contains_encrypted_data`)**:
   - Memastikan bahwa jika kita menggunakan koneksi query SQL mentah (*raw SQL connection*) untuk membaca langsung isi baris database PostgreSQL, data NIK yang tersimpan di kolom fisik benar-benar berupa string acak terenkripsi, bukan teks biasa.

---

## 4. Kisi-Kisi (Hints)

Untuk menyelesaikan tantangan ini:
- **Pustaka Kriptografi**:
  Gunakan kelas `Fernet` dari modul `cryptography.fernet`.
  - Inisialisasi: `f = Fernet(settings.ENCRYPTION_KEY.encode())` (atau gunakan key tiruan untuk keperluan testing).
  - Enkripsi: `f.encrypt(value.encode()).decode()`
  - Dekripsi: `f.decrypt(value.encode()).decode()` (pastikan menangani tipe data byte/string secara tepat).
- **Custom Field Django**:
  - Di dalam `get_prep_value(self, value)`, pastikan Anda memeriksa apakah `value` tidak kosong (`None` atau kosong) sebelum mengenkripsinya.
  - Di dalam `from_db_value(self, value, expression, connection)`, lakukan hal yang sama sebelum mendekripsinya kembali ke string biasa.

---

## 5. Studi Kasus Berpikir Kritis (Critical Thinking Case Study)

1. *Kunci enkripsi (`ENCRYPTION_KEY`) disimpan di berkas konfigurasi env server. Jika penyerang berhasil mendapatkan akses penuh (root access) ke server aplikasi, mereka bisa membaca kunci tersebut dan mendekripsi isi database. Bagaimana cara mengamankan kunci enkripsi tersebut dengan lebih aman di lingkungan produksi skala besar (misal menggunakan Key Management Service seperti AWS KMS, HashiCorp Vault, atau Google Cloud KMS)?*
2. *Bagaimana jika database Anda memiliki jutaan baris data NIK terenkripsi dan Anda perlu melakukan pencarian (search) atau filter data pelanggan berdasarkan NIK-nya? Karena data tersimpan secara acak (terenkripsi), query SQL standard seperti `WHERE NIK = '123...'` tidak akan berfungsi lagi. Solusi arsitektur apa yang bisa digunakan untuk memecahkan masalah pencarian data terenkripsi ini (misalnya menggunakan Blind Index)?*
