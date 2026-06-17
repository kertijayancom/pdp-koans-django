# Learning Notes: Koan 05 - Data Portability & IDOR Protection 🛡️

Tantangan ini berfokus pada prinsip **Portabilitas Data (Data Portability)** dan pencegahan celah keamanan **IDOR/BOLA (Broken Object Level Authorization)** berdasarkan regulasi UU PDP.

---

## 1. Penjelasan Konsep (Concept Explanation)

**Portabilitas Data** adalah hak hukum pengguna (subjek data) untuk mendapatkan salinan data pribadi mereka dalam format yang terstruktur, umum digunakan, dan dapat dibaca oleh mesin (seperti format JSON atau CSV), sehingga mereka dapat memindahkan data tersebut ke layanan lain dengan mudah.

Namun, menyediakan fitur ekspor data pribadi memunculkan celah keamanan yang sangat berbahaya bernama **IDOR (Insecure Direct Object Reference)** atau sekarang sering disebut **BOLA (Broken Object Level Authorization)**:
- Celah keamanan ini terjadi ketika penyerang dapat mengakses data milik pengguna lain hanya dengan menebak/mengubah parameter identitas (seperti ID user atau email) pada endpoint API.
- Untuk mengamankannya, sistem wajib memverifikasi secara ketat bahwa data yang diekspor **hanya milik pengguna yang saat ini sedang login** (*authenticated user context*), bukan data orang lain.

---

## 2. Kenapa Penting (Why It Matters)

Aspek portabilitas data dan keamanan ekspor ini sangat penting karena:
1. **Hak Subjek Data (UU PDP Pasal 7 & 13)**: Subjek data pribadi berhak mendapatkan dan/atau memindahkan data pribadi miliknya dari pengendali data pribadi ke pengendali data pribadi lainnya dalam format yang kompatibel. Kegagalan menyediakan fitur ini melanggar hak hukum dasar mereka.
2. **Mitigasi Kerentanan OWASP Top 10 (BOLA/IDOR)**: BOLA adalah salah satu kerentanan API paling umum dan merusak di dunia. Jika endpoint ekspor data Anda memiliki celah BOLA, penyerang bisa mencuri seluruh data pengguna di sistem hanya dengan melakukan iterasi (skrip *looping*) pada parameter ID pengguna. Hal ini memicu kebocoran data massal yang fatal.

---

## 3. Tingkat Kesulitan (Difficulty Levels)

Tantangan ini dibagi menjadi tiga tingkat kesulitan:

1. **[Basic] Pencegahan IDOR / BOLA (`test_01_basic_prevent_idor_attacks`)**:
   - Memastikan API mendeteksi jika parameter `email` yang diminta berbeda dengan email dari pengguna yang sedang login (`request.user.email`), lalu mengembalikan status `403 Forbidden`.
2. **[Intermediate] Agregasi Data Lintas Tabel (`test_02_intermediate_successful_export_format`)**:
   - Mengumpulkan data profil (`UserProfile`), log persetujuan (`ConsentLog`), dan transaksi belanja (`UserTransaction`) dari database berdasarkan email pengguna saat ini, lalu menyusunnya ke dalam format JSON yang valid.
3. **[Advanced] Asynchronous Data Export (`test_03_advanced_async_export_trigger` & `test_04_advanced_async_export_polling`)**:
   - Menghindari timeout pada ekspor data volume besar. Bila parameter query `async=true` dikirim, sistem segera mengembalikan `202 Accepted` beserta sebuah `job_id` dari model `DataExportJob`.
   - Mengimplementasikan endpoint polling pada `/api/users/export-data/?job_id=<job_id>` untuk melacak status pemrosesan ekspor hingga berubah menjadi `COMPLETED` dan menyediakan tautan unduh data (`download_url`).

---

## 4. Kisi-Kisi (Hints)

### Level Basic
- Dapatkan parameter query `email` dari `request.GET.get('email')`.
- Jika parameter ini ada dan nilainya tidak sama dengan `request.user.email`, kembalikan `Response` dengan status `status.HTTP_403_FORBIDDEN`.

### Level Intermediate
- Cari profil pengguna di database menggunakan `UserProfile.objects.filter(email=user_email).first()`. Tangani dengan aman jika nilainya kosong/tidak ada.
- Kumpulkan daftar persetujuan pengguna dengan `ConsentLog.objects.filter(user_email=user_email)`.
- Kumpulkan daftar transaksi pengguna dengan `UserTransaction.objects.filter(user_email=user_email)`.
- Masukkan data tersebut ke dalam payload JSON akhir:
  ```json
  {
    "profile": { "username": "...", "phone_number": "...", "shipping_address": "..." },
    "consent_logs": [ { "policy_version": "...", "consent_given": true/false, "timestamp": "..." } ],
    "transactions": [ { "item_name": "...", "amount": 0.0, "timestamp": "..." } ]
  }
  ```

### Level Advanced
- Di dalam view, periksa apakah ada parameter `job_id` di query string. Jika ada, lakukan filter pada `DataExportJob` menggunakan `id=job_id` dan `user_email=request.user.email` (untuk mencegah IDOR pada polling). Jika job ditemukan, set statusnya menjadi `COMPLETED`, tentukan tautan unduhannya (misalnya `http://localhost:8000/media/exports/export_<job_id>.json`), lalu simpan dan kembalikan detail job tersebut dengan status `200 OK`.
- Periksa juga parameter `async`. Jika nilainya `"true"`, buat record baru di model `DataExportJob` dengan status `PENDING` untuk pengguna tersebut, lalu kembalikan payload berisi `job_id` dan `status` dengan respons `202 Accepted`.

---

## 5. Studi Kasus Berpikir Kritis (Critical Thinking Case Study)

1. **Skalabilitas dan Volume Data Tinggi**:
   *Bagaimana jika pengguna telah menggunakan layanan Anda selama bertahun-tahun dan memiliki jutaan record transaksi keuangan? Mengagregasikan seluruh data tersebut secara real-time langsung di dalam satu request HTTP sinkron (request-response) akan membuat server kehabisan memori (out of memory) atau mengalami HTTP timeout. Desain arsitektur apa yang lebih aman dan scalable untuk menangani ekspor data berskala besar (misal menggunakan background worker/Celery, penyimpanan sementara ke Cloud Storage, dan pengiriman link download via email)?*
2. **Interoperabilitas Format**:
   *Bagaimana jika pengguna meminta data mereka ditransfer secara otomatis langsung ke server kompetitor bisnis Anda (interoperabilitas)? Standar format data terbuka apa saja yang saat ini umum digunakan di industri untuk mempermudah transfer portabilitas data antar-platform (misal Open Data Standards)?*

