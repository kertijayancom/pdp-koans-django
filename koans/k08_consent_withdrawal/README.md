# Learning Notes: Koan 08 - Consent Withdrawal 🛡️

Tantangan ini berfokus pada prinsip **Penarikan Persetujuan (Consent Withdrawal) & Pembatasan Pemrosesan Aktif** berdasarkan regulasi UU PDP.

---

## 1. Penjelasan Konsep (Concept Explanation)

Dalam aturan pelindungan data pribadi (UU PDP), persetujuan (*consent*) bukanlah jalan satu arah:
- Pengguna yang telah memberikan persetujuan memiliki hak hukum mutlak untuk **menarik kembali persetujuan** tersebut kapan saja (*Consent Withdrawal*).
- Ketika persetujuan ditarik, organisasi Anda wajib **menghentikan pemrosesan aktif** data pribadi pengguna tersebut sesegera mungkin.

Namun, secara teknis aplikasi:
- Menarik persetujuan **tidak sama** dengan menghapus akun secara instan.
- Kita harus mencatat aksi penarikan tersebut sebagai bukti audit trail (`ConsentLog` baru dengan `consent_given = False`).
- Kemudian, kita menonaktifkan kredensial login/akses pengguna (`is_active = False` pada objek User) agar data mereka tidak diproses aktif lagi untuk operasional harian.
- Data historis mereka tetap dipertahankan di database secara aman sampai masa retensi hukumnya (misal: aturan pajak) berakhir, sebelum nantinya benar-benar dihapus secara fisik.

---

## 2. Kenapa Penting (Why It Matters)

Aspek penarikan persetujuan ini sangat penting karena:
1. **Hak Hukum Pengguna (UU PDP Pasal 15 & 40)**: Subjek data pribadi berhak untuk menunda atau membatasi pemrosesan, serta menarik kembali persetujuan pemrosesan data pribadi miliknya. Menolak atau mempersulit pengguna menarik persetujuannya adalah pelanggaran hukum.
2. **Kepatuhan ISO 27001 (Control A.5.15 - Access Control & Consent Management)**: Audit mensyaratkan adanya kendali untuk menolak akses dan membatasi pemrosesan data pribadi sesegera mungkin setelah otorisasi dicabut oleh pemilik data.
3. **Audit Trail Pencabutan**: Anda wajib memiliki bukti terekam tentang *kapan* dan *mengapa* pemrosesan dihentikan demi akuntabilitas saat diaudit oleh otoritas pelindungan data.

---

## 3. Tingkat Kesulitan (Difficulty Levels)

Tantangan ini dibagi menjadi tiga tingkat kesulitan:

1. **[Basic] Penarikan Persetujuan (Consent Withdrawal) (`test_02_basic_consent_withdrawal_success`)**:
   - Mencatat log penarikan persetujuan (`consent_given = False`) di tabel `ConsentLog` untuk email pengguna.
   - Menghentikan pemrosesan aktif secara instan dengan menonaktifkan akun pengguna (`is_active = False`).
2. **[Intermediate] Keamanan Transaksi database (`test_02_basic_consent_withdrawal_success`)**:
   - Memastikan bahwa pencatatan log baru di `ConsentLog` dan deaktivasi user berjalan secara atomik menggunakan Django transaction (`transaction.atomic()`).
   - Mengekstrak informasi penarikan secara akurat (IP Address dari metadata request dan `policy_version` dari payload request).
3. **[Advanced] Pencabutan Sesi Aktif / Blacklisting Token (`test_03_advanced_session_revocation`)**:
   - Untuk memitigasi celah token aktif JWT setelah akun dinonaktifkan, jika parameter `token_jti` disertakan dalam request POST, sistem secara otomatis mendaftarkan token tersebut ke model `RevokedToken` di database (simulasi blacklist session/token).

---

## 4. Kisi-Kisi (Hints)

### Level Basic
- Ambil objek user dari `request.user` dan email dari `user.email`.
- Tambahkan log baru ke tabel `ConsentLog`:
  `ConsentLog.objects.create(user_email=email, consent_given=False, ...)`
- Deaktifkan akun user: `user.is_active = False` dan jalankan `user.save()`.

### Level Intermediate
- Jalankan kode Anda di dalam blok transaksi atomik Django:
  ```python
  from django.db import transaction
  with transaction.atomic():
      # Logika database
  ```
- Dapatkan data IP address dari `request.META.get('REMOTE_ADDR')` dan `policy_version` dari `request.data.get('policy_version')`.

### Level Advanced
- Dapatkan token JTI dari input request: `token_jti = request.data.get('token_jti')`.
- Jika `token_jti` ada, buat entri baru di database untuk membatalkan sesi:
  `RevokedToken.objects.create(user_email=email, token_jti=token_jti)`

---

## 5. Studi Kasus Berpikir Kritis (Critical Thinking Case Study)

1. **JWT Revocation & Token Blacklisting**:
   *Saat pengguna menarik persetujuan mereka dan akunnya dinonaktifkan (`is_active = False`), sesi login aktif (Active Sessions) atau token autentikasi (seperti JWT Access/Refresh Token) yang sudah terlanjur dipegang oleh browser/aplikasi mobile pengguna mungkin masih bisa digunakan sebelum kedaluwarsa. Bagaimana cara Anda memastikan bahwa semua sesi aktif dan token milik pengguna tersebut langsung dicabut secara instan saat persetujuan ditarik (misalnya menggunakan Token Blacklisting)?*
2. **Pub/Sub Microservices Event Sync**:
   *Dalam arsitektur mikroservis, data profil pengguna mungkin direplikasi atau dicache di berbagai layanan independen (misalnya di Redis cache milik layanan Notifikasi). Bagaimana cara Anda menyebarkan status penarikan persetujuan ini ke seluruh mikroservis lain secara real-time agar tidak ada layanan lain yang tidak sengaja mengirimkan email/SMS ke pengguna tersebut setelah persetujuannya ditarik (misal menggunakan Event-Driven Architecture dengan pola Publish-Subscribe)?*

