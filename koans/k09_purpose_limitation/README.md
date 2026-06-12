# Learning Notes: Koan 09 - Purpose Limitation 🛡️

Tantangan ini berfokus pada prinsip **Pembatasan Tujuan Pemrosesan Data (Purpose Limitation)** berdasarkan regulasi UU PDP.

---

## 1. Penjelasan Konsep (Concept Explanation)

**Pembatasan Tujuan (Purpose Limitation)** adalah prinsip tatakelola data yang menyatakan bahwa data pribadi hanya boleh dikumpulkan untuk **tujuan yang spesifik, sah secara hukum, dan transparan**:
- Data pribadi tidak boleh diproses lebih lanjut dengan cara yang tidak kompatibel dengan tujuan awal tersebut.
- Misalnya, ketika pengguna memberikan data nomor telepon dan alamat untuk tujuan **transaksi pengiriman barang**, organisasi Anda tidak boleh menggunakan data tersebut untuk tujuan lain seperti **kampanye iklan promosi/marketing (newsletter/SMS spam)** secara sepihak.

Jika organisasi ingin memproses data tersebut untuk tujuan sekunder (seperti marketing), organisasi wajib meminta persetujuan terpisah secara eksplisit (misal adanya checkbox persetujuan marketing tambahan yang mengubah status profil `marketing_consent = True`). 

Sebelum mengirimkan promosi, sistem wajib melakukan penyaringan (*filter*) ketat di tingkat database untuk memastikan hanya pengguna dengan persetujuan aktif yang dikirimi pesan.

---

## 2. Kenapa Penting (Why It Matters)

Aspek pembatasan tujuan ini sangat krusial karena:
1. **Dampak Hukum (UU PDP Pasal 16 & 27)**: Pemrosesan data pribadi harus disesuaikan dengan tujuan pemrosesan data pribadi. Menyalahgunakan data operasional (transaksional) untuk keperluan promosi komersial tanpa persetujuan tambahan adalah pelanggaran hukum berat.
2. **Kepatuhan ISO 27001 (Control A.5.15 - Access Control & Consent Verification)**: Organisasi harus memverifikasi hak dan tujuan akses data secara sistematis. Kebocoran atau penyalahgunaan data karena tidak adanya filter tujuan penggunaan data sering menjadi temuan audit utama.
3. **Mencegah Keluhan Pengguna (User Complaints)**: Mengirim spam promo kepada pengguna yang tidak merasa mendaftar untuk iklan merusak reputasi perusahaan dan menurunkan tingkat kepuasan pelanggan secara drastis.

---

## 3. Apa yang Test-nya Ajarkan (What the Test Teaches)

Unit test pada Koan 09 memverifikasi kepatuhan sistem dalam membatasi pengiriman promosi:
1. **Verifikasi Hak Akses Dispatcher (`test_non_admin_access_denied`)**:
   - Memastikan bahwa endpoint pengiriman newsletter hanya dapat diakses oleh operator dengan izin tingkat tinggi (`IsAdminUser` / Staf Marketing yang sah). Pengguna biasa tidak boleh memicu pengiriman newsletter massal.
2. **Uji Penyaringan Tujuan (`test_marketing_dispatch_filters_by_purpose_consent`)**:
   - Memverifikasi bahwa daftar email penerima yang dihasilkan oleh API hanya berisi email pengguna yang memiliki atribut `marketing_consent = True`.
   - Memastikan pengguna dengan `marketing_consent = False` (meskipun akun mereka aktif) disaring keluar dan aman dari pengiriman pesan promo.

---

## 4. Kisi-Kisi (Hints)

Untuk menyelesaikan tantangan ini:
- **Izin Akses**:
  Gunakan permission class bawaan dari Django REST Framework `IsAdminUser` untuk membatasi akses endpoint ini hanya kepada administrator/staff.
- **Penyaringan Database (Filtering)**:
  - Lakukan kueri filter pada model `UserProfile` untuk mencari record yang memiliki nilai `marketing_consent` bernilai `True`.
  - Gunakan metode `.values_list('email', flat=True)` pada Django ORM untuk menarik daftar string email saja secara efisien tanpa membebani memori server dengan instansiasi penuh objek model data.
  - Kembalikan daftar tersebut dalam struktur response `{"recipients": list(consented_emails)}`.

---

## 5. Studi Kasus Berpikir Kritis (Critical Thinking Case Study)

1. *Bagaimana jika perusahaan memiliki berbagai jenis kategori promo (misalnya: promo makanan, promo gadget, dan newsletter mingguan)? Memiliki satu flag `marketing_consent` saja tidak cukup karena pengguna mungkin hanya ingin menyetujui promo makanan tapi menolak promo gadget. Bagaimana Anda merancang skema database untuk mendukung manajemen persetujuan yang dinamis dan modular (Granular/Modular Consent Management) sehingga pengguna memiliki kontrol penuh atas kategori iklan yang mereka terima?*
2. *Dalam dunia pemasaran digital, organisasi sering kali menggunakan layanan pihak ketiga untuk mengirim email kampanye massal (seperti Mailchimp atau Sendgrid). Bagaimana Anda merancang arsitektur sinkronisasi data yang aman agar daftar kontak di Sendgrid/Mailchimp selalu sinkron dengan status `marketing_consent` terbaru di database utama kita secara real-time, menghindari terkirimnya email promosi ke pengguna yang baru saja mencabut persetujuannya (opt-out)?*
