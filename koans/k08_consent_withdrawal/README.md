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

## 3. Apa yang Test-nya Ajarkan (What the Test Teaches)

Unit test pada Koan 08 memverifikasi kepatuhan sistem dalam membatasi pemrosesan pasca penarikan persetujuan:
1. **Pemberlakuan Autentikasi (`test_unauthenticated_access_denied`)**:
   - Memastikan hanya pengguna yang sah/terautentikasi yang dapat menarik persetujuannya sendiri.
2. **Pencatatan Audit Trail (`test_consent_withdrawal_success` - Bagian 1)**:
   - Memastikan terbentuknya record `ConsentLog` baru dengan status `consent_given = False` untuk email tersebut.
3. **Pembatasan Pemrosesan Aktif (`test_consent_withdrawal_success` - Bagian 2)**:
   - Memverifikasi bahwa atribut `is_active` pada objek `User` Django berubah menjadi `False`. Hal ini secara instan membatalkan kemampuan mereka untuk melakukan autentikasi/login ke API di masa mendatang.

---

## 4. Kisi-Kisi (Hints)

Untuk menyelesaikan tantangan ini:
- **Pencatatan Log & Deaktivasi**:
  Lakukan modifikasi ini di dalam blok `transaction.atomic()` agar log penarikan persetujuan dan penonaktifan akun disimpan secara bersamaan.
- **Pencatatan Log Baru**:
  Gunakan `ConsentLog.objects.create(...)` untuk membuat baris log baru. Dapatkan alamat IP peminta dari header metadata `request.META.get('REMOTE_ADDR')`.
- **Menonaktifkan User**:
  Ambil objek user saat ini dari `request.user`. Ubah atribut `is_active` menjadi `False`, lalu simpan perubahan tersebut dengan memanggil `.save()`.

---

## 5. Studi Kasus Berpikir Kritis (Critical Thinking Case Study)

1. *Saat pengguna menarik persetujuan mereka dan akunnya dinonaktifkan (`is_active = False`), sesi login aktif (Active Sessions) atau token autentikasi (seperti JWT Access/Refresh Token) yang sudah terlanjur dipegang oleh browser/aplikasi mobile pengguna mungkin masih bisa digunakan sebelum kedaluwarsa. Bagaimana cara Anda memastikan bahwa semua sesi aktif dan token milik pengguna tersebut langsung dicabut secara instan saat persetujuan ditarik (misalnya menggunakan Token Blacklisting)?*
2. *Dalam arsitektur mikroservis, data profil pengguna mungkin direplikasi atau dicache di berbagai layanan independen (misalnya di Redis cache milik layanan Notifikasi). Bagaimana cara Anda menyebarkan status penarikan persetujuan ini ke seluruh mikroservis lain secara real-time agar tidak ada layanan lain yang tidak sengaja mengirimkan email/SMS ke pengguna tersebut setelah persetujuannya ditarik (misal menggunakan Event-Driven Architecture dengan pola Publish-Subscribe)?*
