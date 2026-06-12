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

## 3. Apa yang Test-nya Ajarkan (What the Test Teaches)

Unit test pada Koan 05 menguji aspek keamanan akses dan kelengkapan data hasil ekspor:
1. **Verifikasi Keamanan Konteks (`test_export_other_user_data_returns_forbidden`)**:
   - Memastikan jika seorang pengguna mencoba mengakses data milik pengguna lain (misalnya mengirim parameter email orang lain), API akan langsung menolaknya dengan HTTP status `403 Forbidden`.
   - Ini melatih pengembang untuk tidak pernah mempercayai parameter input yang dikirim client tanpa melakukan asersi kepemilikan data di sisi server.
2. **Kesesuaian Format Ekspor (`test_export_personal_data_success`)**:
   - Memverifikasi bahwa data hasil ekspor dikemas dalam format JSON terstruktur yang valid, serta mengumpulkan seluruh riwayat pengguna dari berbagai tabel (profil pengguna, log consent, dan riwayat transaksi keuangan).

---

## 4. Kisi-Kisi (Hints)

Untuk menyelesaikan tantangan ini:
- **Proteksi Izin**:
  - Ambil parameter email target dari payload request.
  - Bandingkan parameter tersebut dengan email dari pengguna yang sedang login (`request.user.email`).
  - Jika tidak cocok, segera batalkan proses dan kembalikan `Response(status=status.HTTP_403_FORBIDDEN)`.
- **Agregasi Data**:
  - Lakukan kueri ORM untuk mengumpulkan data dari tiga tabel berbeda yang berkaitan dengan email pengguna tersebut:
    1. `UserProfile` (mengambil profil dasar).
    2. `ConsentLog` (mengambil riwayat log persetujuan).
    3. `UserTransaction` (mengambil riwayat transaksi belanja).
  - Susun seluruh data tersebut ke dalam sebuah Python dictionary terstruktur, lalu kembalikan via `Response(data_dict, status=status.HTTP_200_OK)`.

---

## 5. Studi Kasus Berpikir Kritis (Critical Thinking Case Study)

1. *Bagaimana jika pengguna telah menggunakan layanan Anda selama bertahun-tahun dan memiliki jutaan record transaksi keuangan? Mengagregasikan seluruh data tersebut secara real-time langsung di dalam satu request HTTP sinkron (request-response) akan membuat server kehabisan memori (out of memory) atau mengalami HTTP timeout. Desain arsitektur apa yang lebih aman dan scalable untuk menangani ekspor data berskala besar (misal menggunakan background worker/Celery, penyimpanan sementara ke Cloud Storage, dan pengiriman link download via email)?*
2. *Bagaimana jika pengguna meminta data mereka ditransfer secara otomatis langsung ke server kompetitor bisnis Anda (interoperabilitas)? Standar format data terbuka apa saja yang saat ini umum digunakan di industri untuk mempermudah transfer portabilitas data antar-platform (misal Open Data Standards)?*
