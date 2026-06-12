# Learning Notes: Koan 07 - Data Deletion & Anonymisation 🛡️

Tantangan ini berfokus pada prinsip **Penghapusan & Anonimisasi Data Pribadi (Right to be Forgotten)** berdasarkan regulasi UU PDP.

---

## 1. Penjelasan Konsep (Concept Explanation)

Ketika pengguna meminta akun mereka untuk dihapus (*Right to Erasure / Right to be Forgotten*), organisasi Anda dihadapkan pada dua pilihan cara memperlakukan data mereka:
1. **Penghapusan Fisik (Hard-Delete)**:
   - Menghapus secara permanen record data yang secara langsung mengidentifikasi identitas asli pengguna.
   - Contoh: Menghapus data akun login (`User`), profil fisik (`UserProfile`), dan catatan jejak audit persetujuan (`ConsentLog`).
2. **Anonimisasi (Anonymisation)**:
   - Mengubah data pribadi yang terhubung dengan record lain menjadi data acak/samaran sehingga tidak dapat lagi dikaitkan secara fisik dengan individu tertentu.
   - Contoh: Pada data transaksi keuangan (`UserTransaction`), kita tidak menghapus baris transaksinya (karena dibutuhkan untuk laporan keuangan perusahaan dan audit pajak), tetapi kita mengubah field `user_email` menjadi string acak seperti `anonymous_user_a8f9c2d1@pdp.local`.

Dengan pendekatan ini, data keuangan tetap utuh secara agregat, namun hubungan langsung ke privasi individu terputus secara hukum.

---

## 2. Kenapa Penting (Why It Matters)

Aspek penghapusan dan anonimisasi ini sangat penting karena:
1. **Hak Hukum Pengguna (UU PDP Pasal 16 & 43)**: Subjek data pribadi berhak mengakhiri pemrosesan dan meminta penghapusan data pribadinya. Mengabaikan permintaan penghapusan akun secara sengaja adalah pelanggaran hukum berat.
2. **Pengecualian Hukum untuk Transaksi Keuangan**: Organisasi wajib mematuhi hukum perpajakan dan hukum dagang (yang mewajibkan penyimpanan bukti transaksi keuangan selama 5 s.d. 10 tahun). Di sinilah teknik **Anonimisasi** menjadi jembatan penyelamat: Anda mematuhi hak privasi (UU PDP) sekaligus mematuhi hukum keuangan nasional (pajak).
3. **Kepatuhan ISO 27001 (Control A.8.10 / A.8.14)**: Menghapus informasi yang sudah tidak diperlukan lagi oleh bisnis secara sistematis mengurangi area risiko kebocoran data (*risk surface*).

---

## 3. Apa yang Test-nya Ajarkan (What the Test Teaches)

Unit test pada Koan 07 memverifikasi ketepatan eksekusi kedua metode pembersihan tersebut:
1. **Verifikasi Penghapusan Fisik (`test_account_deletion_and_anonymisation` - Bagian 1 & 2)**:
   - Memastikan bahwa model `User`, `UserProfile`, dan `ConsentLog` benar-benar sudah tidak ada lagi di database pasca request penghapusan.
2. **Verifikasi Integritas Transaksi (`test_account_deletion_and_anonymisation` - Bagian 3)**:
   - Memastikan bahwa jumlah data `UserTransaction` di database tetap utuh (tidak berkurang).
   - Memverifikasi bahwa data email pada transaksi berubah format menjadi `anonymous_user_xxxx@pdp.local` (sesuai pola ekspresi reguler anonymisation).

---

## 4. Kisi-Kisi (Hints)

Untuk menyelesaikan tantangan ini:
- **Urutan Operasi & Transaksi**:
  Lakukan modifikasi data di dalam blok transaksi Django (`with transaction.atomic():`). Hal ini sangat krusial karena jika proses penghapusan profil berhasil tetapi anonimisasi transaksi gagal, database akan berada dalam kondisi tidak konsisten.
- **Anonimisasi Terlebih Dahulu**:
  Lakukan pembaruan (`.update(user_email=anon_email)`) pada data `UserTransaction` terlebih dahulu sebelum menghapus akun user. Jika Anda menghapus objek `user` terlebih dahulu, Anda akan kehilangan referensi alamat email asli mereka yang digunakan untuk mem-filter transaksi yang ingin dianomkan.
- **Membuat Email Anonim**:
  Gunakan library bawaan Python `uuid` untuk membuat string acak yang unik agar alamat email tersamar tidak saling bertabrakan:
  `unique_suffix = uuid.uuid4().hex[:8]`

---

## 5. Studi Kasus Berpikir Kritis (Critical Thinking Case Study)

1. *Menganonimkan jutaan baris data transaksi secara sinkron (langsung di dalam kode View API request-response) dapat menyebabkan server hang karena waktu pemrosesan database query yang lama. Bagaimana cara merancang arsitektur pembersihan data secara asinkron (background job) yang aman, di mana status akun langsung berubah "Deleted" untuk pengguna, namun proses pembersihan dan anonimisasi data di database berjalan di latar belakang (Queue worker) secara bertahap?*
2. *Bagaimana jika database Anda direplikasi ke server cadangan (Read Replicas) atau di-backup secara harian (Cold Backup)? Hukum PDP mewajibkan penghapusan data secara menyeluruh. Bagaimana kebijakan dan prosedur teknis Anda untuk memastikan data pribadi yang telah dihapus di database utama juga benar-benar ikut musnah dari file backup lama (misalnya menggunakan Crypto-shredding)?*
