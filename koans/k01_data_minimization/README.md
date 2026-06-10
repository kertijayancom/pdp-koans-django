# Learning Notes: Koan 01 - Data Minimisation 🛡️

Tantangan ini berfokus pada prinsip **Minimisasi Data (Data Minimisation)** sebagaimana diatur dalam regulasi pelindungan data pribadi.

---

## 1. Penjelasan Konsep (Concept Explanation)

**Minimisasi Data** adalah prinsip dasar pelindungan data pribadi yang menyatakan bahwa pengumpulan dan pemrosesan data pribadi harus:
- **Adekuat (Adequate)**: Cukup untuk memenuhi tujuan pemrosesan.
- **Relevan (Relevant)**: Memiliki hubungan langsung dengan tujuan.
- **Terbatas (Limited)**: Hanya mengumpulkan apa yang benar-benar diperlukan (tidak berlebihan).

Dalam konteks e-commerce (kasus kita):
- Pengiriman barang dan transaksi pembayaran **membutuhkan**: nama, email, alamat pengiriman, dan nomor telepon.
- Pengiriman barang **tidak membutuhkan**: agama (*religion*), golongan darah (*blood type*), atau afiliasi politik (*political leaning*).

Selain itu, jika data pribadi harus ditampilkan atau dicatat ke dalam log sistem, data sensitif seperti nomor telepon harus disamarkan (**masked**) agar tidak mudah disalahgunakan oleh pihak yang tidak bertanggung jawab.

---

## 2. Kenapa Penting (Why It Matters)

Mengabaikan prinsip Minimisasi Data mendatangkan risiko besar bagi organisasi Anda:
1. **Dampak Hukum (UU PDP Pasal 16)**: Pemrosesan data yang berlebihan dan tidak relevan melanggar hukum dan dapat dikenai sanksi administratif atau denda finansial yang berat.
2. **Dampak Keamanan (ISO 27001 Control A.8.11 - Data Masking)**: Semakin banyak data yang Anda simpan, semakin besar dampak kerusakan (*blast radius*) jika terjadi kebocoran data (*data breach*). Menyimpan golongan darah atau afiliasi politik pelanggan e-commerce tanpa alasan yang sah adalah bom waktu.
3. **Privasi Pengguna**: Meminta data yang tidak relevan menurunkan tingkat kepercayaan pengguna (*user trust*) terhadap platform Anda.

---

## 3. Apa yang Test-nya Ajarkan (What the Test Teaches)

Unit test pada Koan 01 menguji dua aspek utama untuk menanamkan disiplin ini pada pengembang:
1. **Uji Redundansi Database (`test_db_fields_minimization`)**:
   - Memastikan bahwa kolom-kolom berlebih (`religion`, `blood_type`, `political_leaning`) tidak terdeteksi aktif pada model Django `UserProfile`.
   - Ini mengajarkan kita untuk selalu meninjau ulang skema database dan hanya mempertahankan kolom yang secara operasional memiliki dasar hukum (*lawful basis*) yang sah.
2. **Uji Penyamaran Data (`test_masked_phone_number_property`)**:
   - Memverifikasi properti `masked_phone_number` menyamarkan angka di tengah nomor telepon menjadi karakter asterisk (`*`) tetapi tetap menyisakan 3 angka di depan dan 4 angka di belakang (contoh: `081234567890` -> `081****7890`).
   - Ini melatih pengembang untuk menyamarkan data sensitif sebelum menampilkannya di sisi frontend atau menulisnya ke log audit system (*log masking*).

---

## 4. Kisi-Kisi (Hints)

Untuk menyelesaikan tantangan ini:

- **Bagian A (Skema Database)**: 
  Cukup hapus atau beri komentar (`#`) pada definisi field database yang berlebihan di berkas `models.py`. Django ORM tidak akan memuat field tersebut jika definisinya dihilangkan dari kelas model.
- **Bagian B (Masking String)**:
  - Periksa panjang string nomor telepon sebelum melakukan masking.
  - Anda bisa menggunakan operasi *slicing* string Python sederhana. Ambil 3 karakter pertama, tambahkan asterisk `*` sebanyak panjang karakter yang dihilangkan di tengah, lalu gabungkan dengan 4 karakter terakhir.
  - Rumus dinamis jumlah asterisk: `len(phone_number) - 7`.

---

## 5. Studi Kasus Berpikir Kritis (Critical Thinking Case Study)

1. *Bagaimana jika suatu hari departemen pemasaran meminta kita mengumpulkan data "tanggal lahir" pengguna untuk program promo ulang tahun? Apakah itu melanggar prinsip data minimisation? Bagaimana cara kita memprosesnya secara sah?*
2. *Selain masking nomor telepon, tipe data sensitif apa lagi di e-commerce yang wajib di-masking sebelum ditampilkan di layar admin (misal: nomor kartu kredit, NIK)? Bagaimana Anda akan merancang sistem masking tersebut agar seragam di seluruh aplikasi?*

