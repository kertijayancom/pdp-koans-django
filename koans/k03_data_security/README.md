# Learning Notes: Koan 03 - Data Security & Encryption 🛡️

Tantangan ini berfokus pada prinsip **Keamanan Data & Kriptografi (Encryption At-Rest)** serta pengelolaan masa transisi rotasi kunci enkripsi berdasarkan standar ISO 27001 dan regulasi UU PDP.

---

## 1. Penjelasan Konsep (Concept Explanation)

**Encryption At-Rest** adalah proses menyandikan (mengenkripsi) data sensitif saat disimpan di media penyimpanan fisik (seperti PostgreSQL atau SQLite), sehingga data tidak dapat dibaca tanpa kunci dekripsi yang sah.

Di dalam Koan ini, tantangan dibagi ke dalam **3 tingkat kesulitan (Level)**:
1. **Level 1: Basic (Algoritma Enkripsi Dasar)**: Menggunakan pustaka `cryptography.fernet.Fernet` untuk mengenkripsi dan mendekripsi string dengan kunci simetris AES.
2. **Level 2: Intermediate (Custom Model Field Django ORM)**: Mengintegrasikan fungsi tersebut ke daur hidup ORM Django (`get_prep_value` untuk enkripsi sebelum simpan, `from_db_value` untuk dekripsi setelah baca).
3. **Level 3: Advanced (Rotasi Kunci Enkripsi / Grace Period Decryption)**:
   - Di industri nyata, kunci enkripsi utama (`PRIMARY_KEY`) harus dirotasi secara berkala.
   - Saat rotasi dilakukan, data lama di database masih terenkripsi dengan kunci lama (`FALLBACK_KEYS`).
   - Sistem harus cukup cerdas untuk mencoba mendekripsi menggunakan kunci utama baru terlebih dahulu. Jika gagal (mengalami error `InvalidToken`), sistem otomatis berputar mencoba mendekripsi dengan kunci-kunci lama cadangan (*Grace Period Fallback*).

---

## 2. Kenapa Penting (Why It Matters)

Enkripsi data sensitif di tingkat penyimpanan fisik sangat penting karena:
1. **Dampak Hukum (UU PDP Pasal 39)**: Pengendali data pribadi wajib menjaga keamanan data dari akses yang tidak sah. Menyimpan data sensitif seperti NIK atau nomor kartu kredit dalam bentuk teks biasa (*plain text*) di database adalah bentuk kelalaian hukum yang berat.
2. **Kepatuhan ISO 27001 (Control A.8.24 - Use of Cryptography)**: Standar keamanan informasi mensyaratkan penggunaan kriptografi dan pengelolaan daur hidup kunci (termasuk rotasi kunci berkala).
3. **Mitigasi Kebocoran Cadangan Database (Database Dump Leak)**: Jika berkas cadangan database (*database backup dump*) dicuri oleh penyerang, mereka tetap tidak dapat membacanya tanpa kunci dekripsi yang disimpan terpisah.

---

## 3. Apa yang Test-nya Ajarkan (What the Test Teaches)

Unit test pada Koan 03 memverifikasi integritas dari implementasi enkripsi kita:
1. **[Intermediate] test_01_data_is_encrypted_in_database**:
   - Memastikan bahwa NIK disimpan dalam bentuk terenkripsi di baris tabel fisik database (dites via raw SQL query bypass ORM) tetapi bisa didekripsi dengan kunci utama yang benar.
2. **[Intermediate] test_02_data_is_decrypted_in_orm**:
   - Memastikan ORM Django secara transparan mendekripsi ciphertext kembali menjadi plaintext saat data dibaca kembali oleh aplikasi.
3. **[Advanced] test_03_key_rotation_fallback**:
   - Memastikan data lama yang dienkripsi menggunakan kunci cadangan (`FALLBACK_KEYS`) masih tetap bisa didekripsi dengan sukses oleh sistem, meskipun kunci utama aplikasi saat ini sudah berubah.

---

## 4. Kisi-Kisi (Hints)

Untuk menyelesaikan tantangan ini:
- **[Basic & Intermediate] Enkripsi Dasar**:
  - Gunakan `Fernet(PRIMARY_KEY)`.
  - Enkripsi: `f.encrypt(value.encode('utf-8')).decode('utf-8')`
  - Dekripsi: `f.decrypt(value.encode('utf-8')).decode('utf-8')`
- **[Advanced] Key Rotation Decryption di `from_db_value`**:
  - Bungkus logika dekripsi utama dengan blok penanganan error `try-except`.
  - Jika mendekripsi dengan `PRIMARY_KEY` memicu error `InvalidToken` (impor dari `cryptography.fernet`), buat loop `for key in FALLBACK_KEYS`.
  - Coba dekripsi value menggunakan `Fernet(key)`. Jika berhasil, langsung kembalikan hasilnya. Jika gagal, lanjutkan ke kunci berikutnya.

---

## 5. Studi Kasus Berpikir Kritis (Critical Thinking Case Study)

1. *Kunci enkripsi (`PRIMARY_KEY`) disimpan di berkas konfigurasi env server. Jika penyerang berhasil mendapatkan akses penuh (root access) ke server aplikasi, mereka bisa membaca kunci tersebut dan mendekripsi isi database. Bagaimana cara mengamankan kunci enkripsi tersebut dengan lebih aman di lingkungan produksi skala besar (misal menggunakan Key Management Service seperti AWS KMS, HashiCorp Vault, atau Google Cloud KMS)?*
2. *Bagaimana jika database Anda memiliki jutaan baris data NIK terenkripsi dan Anda perlu melakukan pencarian (search) atau filter data pelanggan berdasarkan NIK-nya? Karena data tersimpan secara acak (terenkripsi), query SQL standard seperti `WHERE NIK = '123...'` tidak akan berfungsi lagi. Solusi arsitektur apa yang bisa digunakan untuk memecahkan masalah pencarian data terenkripsi ini (misalnya menggunakan Blind Index)?*
