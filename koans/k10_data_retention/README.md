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

## 3. Apa yang Test-nya Ajarkan (What the Test Teaches)

Unit test pada Koan 10 memverifikasi ketepatan logika penghapusan dan format umpan balik CLI command:
1. **Uji Selektivitas Penghapusan (`test_purge_expired_logs_command` - Bagian 1)**:
   - Memastikan bahwa log yang umurnya sudah melebihi batas waktu (seperti log usia 45 hari dan 60 hari pada skenario retensi 30 hari) benar-benar terhapus secara permanen dari tabel `ActionAuditLog`.
   - Memastikan log yang masih baru (berusia di bawah 30 hari) tetap dipertahankan dan aman dari proses pembersihan.
2. **Kesesuaian Output Console (`test_purge_expired_logs_command` - Bagian 2)**:
   - Memverifikasi bahwa skrip CLI mencetak informasi status hasil pembersihan ke standard output dengan format yang tepat: `"Deleted X expired log records."`.

---

## 4. Kisi-Kisi (Hints)

Untuk menyelesaikan tantangan ini:
- **Menghitung Batas Waktu (Threshold Date)**:
  - Gunakan `timezone.now()` (bawaan Django) untuk mendapatkan waktu server saat ini.
  - Kurangi waktu saat ini dengan parameter jumlah hari yang diberikan menggunakan kelas `timedelta` dari modul `datetime`.
  - Contoh rumus: `threshold_date = timezone.now() - timedelta(days=days)`.
- **Query Filter & Delete**:
  - Lakukan filter pada data `ActionAuditLog` yang memiliki kolom `timestamp` lebih kecil dari batas waktu (`timestamp__lt=threshold_date`).
  - Panggil fungsi `.delete()` pada queryset hasil filter tersebut.
  - Fungsi `.delete()` akan mengembalikan tuple. Ambil elemen pertama dari tuple tersebut untuk mendapatkan jumlah baris yang berhasil dihapus (`deleted_count`).
- **Mencetak Hasil**:
  Gunakan pemanggilan `self.stdout.write(...)` untuk mencetak pesan hasil ke console output Django Command.

---

## 5. Studi Kasus Berpikir Kritis (Critical Thinking Case Study)

1. *Dalam sistem berskala besar, menjalankan query `DELETE` massal untuk jutaan data sekaligus dapat mengunci database (Table Lock), meningkatkan penggunaan CPU hingga 100%, dan mengganggu transaksi aktif pengguna. Bagaimana cara Anda mendesain skrip penghapusan berkala tersebut agar berjalan secara bertahap (Batch Deletion / Chunking) sehingga database tetap responsif (misal: menghapus maksimal 1000 baris per iterasi dengan jeda istirahat/sleep beberapa detik)?*
2. *Bagaimana jika data yang ingin dimusnahkan tidak boleh dihapus secara fisik karena masih dibutuhkan oleh tim Data Science untuk analitik perilaku jangka panjang, namun kita tetap harus mematuhi UU PDP untuk menghapus identitas pribadi? Bagaimana Anda merancang arsitektur Anonymisation Pipeline di mana data produksi di-copy ke Data Warehouse/Data Lake, lalu disaring untuk menghilangkan seluruh kolom data pribadi sebelum log aslinya di database produksi dimusnahkan secara fisik (Cold Storage)?*
