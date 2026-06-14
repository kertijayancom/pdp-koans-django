# Learning Notes: Koan 02 - Explicit Consent 🛡️

Tantangan ini berfokus pada prinsip **Dasar Pemrosesan & Bukti Persetujuan (Explicit Consent & Consent Logging)** serta pemisahan persetujuan (**Consent Unbundling**) berdasarkan regulasi pelindungan data pribadi (UU PDP Pasal 20 & 21 jo. RPP Pasal 55).

---

## 1. Penjelasan Konsep (Concept Explanation)

Dalam aturan pelindungan data pribadi (UU PDP), salah satu dasar hukum (*lawful basis*) yang sah untuk memproses data pribadi seseorang adalah adanya **Persetujuan (Consent)** yang diberikan secara sadar dan eksplisit oleh subjek data.

Persetujuan ini harus memenuhi tiga prinsip penting yang diuji di Koan ini:
1. **Level 1: Basic (Validasi Persetujuan Utama)**: Registrasi layanan inti membutuhkan persetujuan Syarat & Ketentuan (`consent_service = True`). Jika ini ditolak, layanan tidak dapat diberikan.
2. **Level 2: Intermediate (Recorded/Audit Trail)**: Organisasi wajib merekam bukti persetujuan ke tabel `ConsentLog` lengkap dengan IP address, timestamp, dan versi kebijakan privasi (`policy_version`) sebagai bukti audit yang sah.
3. **Level 3: Advanced (Consent Unbundling)**: Dilarang menyatukan (*bundling*) persetujuan Syarat & Ketentuan layanan inti dengan persetujuan sekunder seperti menerima SMS/email promosi pemasaran (`consent_marketing`). Pengguna harus tetap bisa mendaftar layanan meskipun mereka menolak menerima iklan.

---

## 2. Kenapa Penting (Why It Matters)

Mengapa unbundling consent dan pencatatan log ini sangat krusial?
1. **Beban Pembuktian (UU PDP Pasal 21)**: Jika suatu hari ada sengketa, beban pembuktian berada di tangan organisasi Anda. Anda harus bisa membuktikan kapan dan bagaimana user memberikan persetujuan mereka. Jika log ini tidak ada, Anda dianggap memproses data secara ilegal.
2. **Keabsahan Persetujuan (RPP Pasal 55)**: Persetujuan tidak sah jika dijadikan syarat untuk mendapatkan layanan utama padahal pemrosesan data tersebut tidak mutlak diperlukan untuk layanan tersebut (seperti memaksa setuju menerima newsletter promo sebagai syarat pembuatan rekening bank/akun e-commerce).
3. **Kepatuhan ISO 27001 (Control A.5.15 - Access Control & Consent Management)**: Mengelola penolakan promosi secara sistematis di tingkat database mengurangi komplain pengguna dan menjaga kebersihan data pemasaran.

---

## 3. Apa yang Test-nya Ajarkan (What the Test Teaches)

Unit test pada Koan 02 menguji perilaku sistem saat proses registrasi/pendaftaran akun:
1. **[Basic] test_01_reject_without_consent**:
   - Memastikan bahwa jika request registrasi dikirimkan dengan parameter `consent_service = False`, API wajib menolaknya dan mengembalikan HTTP status `400 Bad Request`.
2. **[Intermediate] test_02_accept_and_log_consent**:
   - Memastikan jika registrasi sukses, sistem secara otomatis membuat entry baru di tabel `ConsentLog` yang memuat IP address client dan versi kebijakan privasi dengan benar.
3. **[Advanced] test_03_consent_unbundling_success**:
   - Memverifikasi bahwa registrasi tetap berhasil (`201 Created`) saat `consent_marketing = False` (selama `consent_service = True`). Test memverifikasi bahwa profil user terbuat dengan status `marketing_consent = False`.
4. **[Advanced] test_04_consent_unbundling_marketing_granted**:
   - Memverifikasi bahwa jika user mencentang setuju promosi (`consent_marketing = True`), profil user terbuat dengan status `marketing_consent = True`.

---

## 4. Kisi-Kisi (Hints)

Untuk menyelesaikan tantangan ini:
- **Validasi & Pemisahan**:
  - Ambil parameter dari request payload: `consent_service`, `consent_marketing`, dan `email`.
  - Jika `consent_service` bukan boolean `True`, kembalikan `Response(status=status.HTTP_400_BAD_REQUEST)`.
- **Pembuatan Log & Profil**:
  - Bungkus logika di dalam `with transaction.atomic():` (impor dari `django.db`) untuk menjamin konsistensi.
  - Catat persetujuan layanan utama di `ConsentLog`. Dapatkan IP address menggunakan `request.META.get('REMOTE_ADDR')`.
  - Daftarkan akun (atau dalam hal ini buat profile `UserProfile` dari k01) dan set kolom `marketing_consent` secara dinamis bernilai sesuai input boolean `consent_marketing`.
  - Kembalikan `Response(status=status.HTTP_201_CREATED)`.

---

## 5. Studi Kasus Berpikir Kritis (Critical Thinking Case Study)

1. *Bayangkan sebuah skenario di mana perusahaan merilis versi Kebijakan Privasi baru (misal dari v1.0 ke v1.1) karena ada fitur baru. Bagaimana sistem Anda mendeteksi pengguna lama yang belum menyetujui versi v1.1? Apakah mereka harus diblokir langsung saat login, atau diberi pop-up persetujuan saat membuka aplikasi?*
2. *Bagaimana jika pengguna menuntut bahwa mereka tidak pernah memberikan persetujuan, dan mengklaim bahwa data log di database kita dimanipulasi oleh administrator internal? Bagaimana Anda dapat membuktikan keaslian audit log tersebut dari sisi keamanan informasi (misalnya menggunakan hashing atau tanda tangan digital)?*
