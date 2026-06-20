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

## 3. Tingkat Kesulitan (Difficulty Levels)

Tantangan ini dibagi menjadi tiga tingkat kesulitan:

1. **[Basic] Penyaringan Tujuan Umum (`test_01_basic_marketing_dispatch_filters_by_general_consent`)**:
   - Membatasi akses endpoint hanya untuk pengguna admin/staf (`IsAdminUser`).
   - Menyaring data `UserProfile` untuk mendapatkan daftar email yang menyetujui komunikasi pemasaran umum (`marketing_consent = True`).
2. **[Intermediate] Penyaringan Persetujuan Granular / Kategori (`test_02_intermediate_marketing_dispatch_by_granular_category`)**:
   - Mendukung kampanye iklan modular. Jika request membawa parameter `category` (misal: `weekly_newsletter`), lakukan penyaringan menggunakan tabel pencocokan persetujuan granular `GranularMarketingConsent` di database di mana `consent_given = True` untuk kategori tersebut.
3. **[Advanced] Pengecekan Kepatuhan Menyeluruh (`test_03_advanced_marketing_dispatch_excludes_inactive_or_compromised`)**:
   - Menjamin bahwa sistem tidak akan pernah mengirimkan iklan promosi ke akun yang tidak aktif (`is_active = False` di database auth Django) atau akun yang sedang terkompromi (`is_compromised = True` di database `CompromisedUser`), bahkan jika mereka memiliki persetujuan iklan yang aktif.

---

## 4. Kisi-Kisi (Hints)

### Level Basic
- Gunakan DRF Permission `IsAdminUser` pada view.
- Ambil semua email pengguna yang menyetujui pemasaran:
  `UserProfile.objects.filter(marketing_consent=True).values_list('email', flat=True)`

### Level Intermediate
- Periksa payload input request: `category = request.data.get('category')`.
- Jika `category` diisi, filter pada model `GranularMarketingConsent`:
  `GranularMarketingConsent.objects.filter(category=category, consent_given=True).values_list('user_email', flat=True)`

### Level Advanced
- Di luar pemeriksaan persetujuan, dapatkan daftar pengecualian (exclude):
  - User tidak aktif: `User.objects.filter(is_active=False).values_list('email', flat=True)`
  - User terkompromi: `CompromisedUser.objects.filter(is_compromised=True).values_list('user_email', flat=True)`
- Lakukan penyaringan pada list akhir untuk mengeluarkan email yang masuk ke dalam daftar pengecualian di atas.

---

## 5. Studi Kasus Berpikir Kritis (Critical Thinking Case Study)

1. **Desain Database Granular Consent**:
   *Bagaimana jika perusahaan memiliki berbagai jenis kategori promo (misalnya: promo makanan, promo gadget, dan newsletter mingguan)? Memiliki satu flag `marketing_consent` saja tidak cukup karena pengguna mungkin hanya ingin menyetujui promo makanan tapi menolak promo gadget. Bagaimana Anda merancang skema database untuk mendukung manajemen persetujuan yang dinamis dan modular (Granular/Modular Consent Management) sehingga pengguna memiliki kontrol penuh atas kategori iklan yang mereka terima?*
2. **Sinkronisasi Pihak Ketiga (Third-Party Sync)**:
   *Dalam dunia pemasaran digital, organisasi sering kali menggunakan layanan pihak ketiga untuk mengirim email kampanye massal (seperti Mailchimp atau Sendgrid). Bagaimana Anda merancang arsitektur sinkronisasi data yang aman agar daftar kontak di Sendgrid/Mailchimp selalu sinkron dengan status `marketing_consent` terbaru di database utama kita secara real-time, menghindari terkirimnya email promosi ke pengguna yang baru saja mencabut persetujuannya (opt-out)?*

