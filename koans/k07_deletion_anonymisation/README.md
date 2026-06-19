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

## 3. Tingkat Kesulitan (Difficulty Levels)

Tantangan ini dibagi menjadi tiga tingkat kesulitan:

1. **[Basic] Penghapusan Fisik (Hard-Delete) (`test_02_basic_hard_delete`)**:
   - Menghapus secara permanen data langsung identitas pengguna (`User`, `UserProfile`, dan `ConsentLog`) dari database pasca permohonan penghapusan akun.
2. **[Intermediate] Anonimisasi Transaksi Historis (`test_03_intermediate_deletion_and_anonymisation`)**:
   - Melakukan anonimisasi pada data transaksi finansial (`UserTransaction`) dengan mengubah field `user_email` menjadi `anonymous_user_<uuid>@pdp.local` tanpa menghapus baris transaksi demi menjaga integritas data keuangan perusahaan.
   - Menjamin integritas pemrosesan dengan membungkus operasi penghapusan dan anonimisasi dalam satu transaksi database atomik (`transaction.atomic()`).
3. **[Advanced] Asynchronous Delayed Deletion (`test_04_advanced_delayed_deletion_trigger`)**:
   - Menyediakan fitur penghapusan tertunda secara asinkron untuk menangani data skala besar. Jika parameter `delayed=true` dikirim via query string:
     - Buat catatan permintaan baru di model `DeletionRequest` dengan status `PENDING`.
     - Matikan akses user ke sistem secara instan dengan mengubah properti `is_active = False` pada objek user (soft-delete), tanpa melakukan penghapusan fisik secara sinkron.
     - Kembalikan respons HTTP `202 Accepted`.

---

## 4. Kisi-Kisi (Hints)

### Level Basic
- Hapus data profile pengguna dengan `UserProfile.objects.filter(email=email).delete()`.
- Hapus log persetujuan dengan `ConsentLog.objects.filter(user_email=email).delete()`.
- Hapus akun pengguna dengan `user.delete()`.

### Level Intermediate
- Gunakan blok transaksi atomik:
  ```python
  from django.db import transaction
  with transaction.atomic():
      # Logika pembaruan & penghapusan data
  ```
- Lakukan anonimisasi transaksi sebelum user dihapus:
  ```python
  import uuid
  unique_suffix = uuid.uuid4().hex[:8]
  anon_email = f"anonymous_user_{unique_suffix}@pdp.local"
  UserTransaction.objects.filter(user_email=email).update(user_email=anon_email)
  ```

### Level Advanced
- Cek jika parameter query `delayed` bernilai `'true'`:
  - Buat baris baru di `DeletionRequest` dengan status `'PENDING'`.
  - Ubah status user: `user.is_active = False` dan jalankan `user.save()`.
  - Kembalikan `Response` dengan status `status.HTTP_202_ACCEPTED`.

---

## 5. Studi Kasus Berpikir Kritis (Critical Thinking Case Study)

1. **Pemrosesan Data Skala Besar (Batch Processing)**:
   *Menganonimkan jutaan baris data transaksi secara sinkron (langsung di dalam kode View API request-response) dapat menyebabkan server hang karena waktu pemrosesan database query yang lama. Bagaimana cara merancang arsitektur pembersihan data secara asinkron (background job) yang aman, di mana status akun langsung berubah "Deleted" untuk pengguna, namun proses pembersihan dan anonimisasi data di database berjalan di latar belakang (Queue worker) secara bertahap?*
2. **Penghapusan Cadangan (Cold Backups & Crypto-shredding)**:
   *Bagaimana jika database Anda direplikasi ke server cadangan (Read Replicas) atau di-backup secara harian (Cold Backup)? Hukum PDP mewajibkan penghapusan data secara menyeluruh. Bagaimana kebijakan dan prosedur teknis Anda untuk memastikan data pribadi yang telah dihapus di database utama juga benar-benar ikut musnah dari file backup lama (misalnya menggunakan Crypto-shredding)?*

