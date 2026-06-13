# Learning Notes: Koan 01 - Data Minimisation 🛡️

Tantangan ini berfokus pada prinsip **Minimisasi Data (Data Minimisation)** sebagaimana diatur dalam regulasi pelindungan data pribadi (UU PDP Pasal 16 & ISO 27001 Control A.8.11).

---

## 1. Penjelasan Konsep (Concept Explanation)

**Minimisasi Data** adalah prinsip dasar pelindungan data pribadi yang menyatakan bahwa pengumpulan dan pemrosesan data pribadi harus:
- **Adekuat (Adequate)**: Cukup untuk memenuhi tujuan pemrosesan.
- **Relevan (Relevant)**: Memiliki hubungan langsung dengan tujuan.
- **Terbatas (Limited)**: Hanya mengumpulkan apa yang benar-benar diperlukan (tidak berlebihan).

Di dalam Koan ini, tantangan dibagi ke dalam **3 tingkat kesulitan (Level)**:
1. **Level 1: Basic (Masking String Dasar)**: Menyamarkan data nomor telepon di tingkat aplikasi agar aman saat ditampilkan/dicatat di log.
2. **Level 2: Intermediate (Context-Aware Masking)**: Menyamarkan nomor telepon secara dinamis. Jika diakses oleh pengguna biasa, tampilkan nomor tersamar. Jika diakses oleh Staff/DPO, tampilkan nomor telepon asli.
3. **Level 3: Advanced (Database Schema Drop)**: Menghapus definisi field dari kode models.py DAN memastikan kolom-kolom tersebut benar-benar di-drop secara fisik dari database PostgreSQL/SQLite melalui perintah migrasi.

---

## 2. Kenapa Penting (Why It Matters)

Mengabaikan prinsip Minimisasi Data mendatangkan risiko besar bagi organisasi Anda:
1. **Dampak Hukum (UU PDP Pasal 16)**: Pemrosesan data yang berlebihan dan tidak relevan melanggar hukum dan dapat dikenai sanksi administratif atau denda finansial yang berat.
2. **Dampak Keamanan (ISO 27001 Control A.8.11 - Data Masking)**: Semakin banyak data yang Anda simpan, semakin besar dampak kerusakan (*blast radius*) jika terjadi kebocoran data (*data breach*). Menyimpan golongan darah atau afiliasi politik pelanggan e-commerce tanpa alasan yang sah adalah bom waktu.
3. **Privasi Pengguna**: Meminta data yang tidak relevan menurunkan tingkat kepercayaan pengguna (*user trust*) terhadap platform Anda.

---

## 3. Apa yang Test-nya Ajarkan (What the Test Teaches)

Unit test pada Koan 01 menguji aspek-aspek berikut:
1. **[Advanced] test_01_excessive_fields_removed**:
   - Memastikan definisi field `religion`, `blood_type`, dan `political_leaning` sudah dihapus dari kode model Django `UserProfile`.
2. **[Basic] test_02_phone_number_masked_correctly**:
   - Memverifikasi properti `masked_phone_number` menyamarkan bagian tengah nomor telepon dengan karakter asterisk (`*`) tetapi tetap menyisakan 3 angka di depan dan 4 angka di belakang.
3. **[Intermediate] test_03_context_aware_masking**:
   - Memastikan bahwa metode `get_masked_phone_number(requesting_user)` mengenali peran pengakses. Hanya DPO (`is_dpo = True`) dan Staff (`is_staff = True`) yang berwenang melihat data asli untuk keperluan kerja, sisanya diblokir (mendapatkan hasil masking).
4. **[Advanced] test_04_database_dropped_columns**:
   - Memverifikasi langsung ke skema fisik database menggunakan raw SQL query untuk memastikan kolom berlebih benar-benar telah di-drop dari tabel PostgreSQL/SQLite.

---

## 4. Kisi-Kisi (Hints)

Untuk menyelesaikan tantangan ini:

- **[Basic] Masking Logic**:
  Gunakan operasi *slicing* string Python sederhana. Ambil 3 karakter pertama, tambahkan asterisk `*` sebanyak `len(phone_number) - 7`, lalu gabungkan dengan 4 karakter terakhir.
- **[Intermediate] Context-Aware**:
  Di dalam metode `get_masked_phone_number(self, requesting_user)`:
  - Cek apakah `requesting_user.is_staff` bernilai `True`, ATAU `getattr(requesting_user, 'is_dpo', False)` bernilai `True`.
  - Jika ya, kembalikan `self.phone_number`. Jika tidak, kembalikan `self.masked_phone_number`.
- **[Advanced] Database Physical Drop**:
  - Hapus kolom `religion`, `blood_type`, dan `political_leaning` di `models.py`.
  - Jalankan perintah pembuatan migrasi dan eksekusi migrasi di dalam kontainer Docker Anda:
    ```bash
    docker-compose exec web python manage.py makemigrations
    docker-compose exec web python manage.py migrate
    ```

---

## 5. Studi Kasus Berpikir Kritis (Critical Thinking Case Study)

1. *Bagaimana jika suatu hari departemen pemasaran meminta kita mengumpulkan data "tanggal lahir" pengguna untuk program promo ulang tahun? Apakah itu melanggar prinsip data minimisation? Bagaimana cara kita memprosesnya secara sah? (Pikirkan mengenai pemisahan database tabel marketing, dan hanya menyimpan Hari & Bulan tanpa menyimpan Tahun lahir).*
2. *Selain masking nomor telepon, tipe data sensitif apa lagi di e-commerce yang wajib di-masking sebelum ditampilkan di layar admin (misal: nomor kartu kredit, NIK)? Bagaimana Anda akan merancang sistem masking tersebut agar seragam di seluruh aplikasi?*
