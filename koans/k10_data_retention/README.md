# Learning Notes: Koan 10 - Data Retention Policy 🛡️

Tantangan ini berfokus pada prinsip **Kebijakan Retensi Data & Otomatisasi Pemusnahan Data (Data Retention Policy)** berdasarkan standar ISO 27001 dan regulasi UU PDP.

---

## 1. Penjelasan Konsep (Concept Explanation)

**Kebijakan Retensi Data (Data Retention Policy)** menetapkan jangka waktu maksimum organisasi Anda diizinkan untuk menyimpan jenis data pribadi tertentu:
- Data pribadi tidak boleh disimpan tanpa batas waktu (*indefinitely*) jika tujuan pemrosesan awalnya sudah selesai.
- Setelah jangka waktu retensi habis (misal: log audit keamanan/login hanya boleh disimpan maksimal 1 tahun), data tersebut wajib dimusnahkan secara permanen atau dihapus dari sistem.

Secara teknis di tingkat aplikasi:
- Proses pemusnahan ini biasanya diotomatisasi menggunakan tugas latar belakang yang dijadwalkan secara berkala (**Scheduled/Background Tasks**).
- Di Django, kita mengimplementasikannya melalui **Custom Management Command** (skrip Python yang bisa dieksekusi via CLI `python manage.py purge_expired_logs --days=X`). Skrip ini akan dijalankan secara otomatis setiap malam melalui utilitas sistem seperti Cron Job.

---

## 2. Kenapa Penting (Why It Matters)

Kebijakan retensi dan pemusnahan data otomatis ini sangat penting karena:
1. **Kewajiban Hukum Pemusnahan (UU PDP Pasal 16 & 43)**: Pengendali data pribadi wajib memusnahkan data pribadi jika masa retensinya telah berakhir atau tujuan pemrosesannya telah tercapai. Menyimpan data pribadi secara sengaja melebihi masa retensi melanggar hukum.
2. **Kepatuhan ISO 27001 (Control A.8.10 - Information Deletion)**: Standar keamanan mensyaratkan pemusnahan informasi sensitif secara teratur saat masa pakainya habis untuk mencegah kebocoran data.
3. **Meminimalkan Blast Radius (Dampak Peretasan)**: Jika penyerang berhasil menembus sistem Anda, dampak kebocoran akan jauh lebih kecil jika Anda hanya menyimpan log 1 tahun terakhir dibandingkan jika Anda menyimpan seluruh log sejarah sistem sejak 10 tahun lalu.
4. **Efisiensi Penyimpanan (Storage Efficiency)**: Menghapus data sampah yang sudah usang mengurangi biaya penyimpanan cloud dan mempercepat kinerja kueri database utama Anda.

---

## 3. Tingkat Kesulitan (Difficulty Levels)

Tantangan ini dibagi menjadi tiga tingkat kesulitan:

1. **[Basic] Pembersihan Log Kedaluwarsa (`test_01_basic_purge_expired_logs`)**:
   - Menghitung batas waktu (*threshold date*) berdasarkan parameter `--days` (default 365).
   - Menghapus secara fisik record `ActionAuditLog` yang kedaluwarsa dan menulis output log `"Deleted X expired log records."` ke standard output CLI.
2. **[Intermediate] Batch Deletion / Chunking (`test_02_intermediate_chunked_deletion`)**:
   - Untuk menghindari penguncian tabel database pada log berskala besar, lakukan proses pembersihan secara bertahap menggunakan limit berukuran `--chunk-size` (default 1000) di dalam sebuah perulangan/loop hingga semua data kedaluwarsa terhapus.
3. **[Advanced] Archival Policy / Cold Storage (`test_03_advanced_archival_before_deletion`)**:
   - Mendukung kebijakan pengarsipan legal. Jika parameter `--archive` disertakan, sistem wajib mengekspor dan menyimpan data log yang kedaluwarsa ke dalam format file JSON di dalam folder `koans/k10_data_retention/archives/` sebelum data fisik tersebut dihapus permanen.
   - Output log CLI harus berubah menjadi `"Archived and deleted X expired log records."`.

---

## 4. Kisi-Kisi (Hints)

### Level Basic
- Hitung batas tanggal kedaluwarsa:
  `threshold_date = timezone.now() - timedelta(days=days)`
- Hapus semua data yang memiliki timestamp lebih kecil dari batas:
  `ActionAuditLog.objects.filter(timestamp__lt=threshold_date).delete()`
- Tulis respons ke stdout:
  `self.stdout.write(f"Deleted {X} expired log records.")`

### Level Intermediate
- Hapus data secara bertahap di dalam perulangan `while True:`:
  1. Dapatkan list PK (ID) dari chunk pertama:
     `expired_pks = list(ActionAuditLog.objects.filter(timestamp__lt=threshold_date).values_list('pk', flat=True)[:chunk_size])`
  2. Jika `expired_pks` kosong, hentikan perulangan (`break`).
  3. Lakukan penghapusan berdasarkan list PK tersebut:
     `deleted_count, _ = ActionAuditLog.objects.filter(pk__in=expired_pks).delete()`

### Level Advanced
- Di awal method `handle()`, cek apakah `--archive` bernilai `True`.
- Jika ya, buat folder archives jika belum ada:
  ```python
  import os
  archive_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'archives')
  os.makedirs(archive_dir, exist_ok=True)
  ```
- Sebelum proses hapus dimulai, kumpulkan dan konversikan objek data log yang kedaluwarsa ke tipe serialisasi JSON, lalu tulis ke berkas arsip menggunakan `json.dump()`.

---

## 5. Studi Kasus Berpikir Kritis (Critical Thinking Case Study)

1. **Batch Deletion (Lock Prevention)**:
   *Dalam sistem berskala besar, menjalankan query `DELETE` massal untuk jutaan data sekaligus dapat mengunci database (Table Lock), meningkatkan penggunaan CPU hingga 100%, dan mengganggu transaksi aktif pengguna. Bagaimana cara Anda mendesain skrip penghapusan berkala tersebut agar berjalan secara bertahap (Batch Deletion / Chunking) sehingga database tetap responsif (misal: menghapus maksimal 1000 baris per iterasi dengan jeda istirahat/sleep beberapa detik)?*
2. **Anonymisation Pipelines (Data Warehousing)**:
   *Bagaimana jika data yang ingin dimusnahkan tidak boleh dihapus secara fisik karena masih dibutuhkan oleh tim Data Science untuk analitik perilaku jangka panjang, namun kita tetap harus mematuhi UU PDP untuk menghapus identitas pribadi? Bagaimana Anda merancang arsitektur Anonymisation Pipeline di mana data produksi di-copy ke Data Warehouse/Data Lake, lalu disaring untuk menghilangkan seluruh kolom data pribadi sebelum log aslinya di database produksi dimusnahkan secara fisik (Cold Storage)?*

