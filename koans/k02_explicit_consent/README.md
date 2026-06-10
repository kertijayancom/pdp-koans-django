# Learning Notes: Koan 02 - Explicit Consent 🛡️

Tantangan ini berfokus pada prinsip **Dasar Pemrosesan & Bukti Persetujuan (Explicit Consent & Consent Logging)** berdasarkan regulasi pelindungan data pribadi.

---

## 1. Penjelasan Konsep (Concept Explanation)

Dalam aturan pelindungan data pribadi (UU PDP), salah satu dasar hukum (*lawful basis*) yang sah untuk memproses data pribadi seseorang adalah adanya **Persetujuan (Consent)** yang diberikan secara sadar dan eksplisit oleh subjek data.

Persetujuan ini harus memenuhi syarat:
- **Eksplisit (Explicit)**: Tindakan aktif dari pengguna (misalnya, mencentang checkbox persetujuan), bukan persetujuan pasif (seperti mencentang otomatis sejak awal atau sekadar tulisan "Dengan mendaftar Anda menyetujui...").
- **Terekam (Recorded/Audit Trail)**: Organisasi wajib memiliki bukti terekam bahwa persetujuan tersebut benar-benar telah diberikan oleh pengguna yang bersangkutan.

Bukti persetujuan ini biasanya disimpan ke dalam tabel khusus (**Consent Log**) yang mencatat:
- **Email/Identitas** pengguna yang memberikan persetujuan.
- **Status Persetujuan** (True/False).
- **IP Address** asal request (sebagai bukti digital/audit trail lokasi/jaringan saat consent diberikan).
- **Waktu** ketika consent diberikan (timestamp).
- **Versi Kebijakan Privasi** yang disetujui (misal: `v1.0`), karena jika kebijakan privasi berubah, Anda perlu meminta persetujuan ulang.

---

## 2. Kenapa Penting (Why It Matters)

Mengapa pencatatan consent secara eksplisit ini sangat krusial?
1. **Beban Pembuktian (UU PDP Pasal 21)**: Jika suatu hari ada sengketa atau audit dari otoritas pelindungan data pribadi, beban pembuktian berada di tangan organisasi Anda. Anda harus bisa membuktikan kapan dan bagaimana user memberikan persetujuan mereka. Jika log ini tidak ada, Anda dianggap memproses data secara ilegal.
2. **Kepatuhan ISO 27001 (Control A.5.15 - Access Control & Consent Management)**: Audit keamanan informasi mensyaratkan adanya mekanisme terdokumentasi dan terkontrol dalam mengelola persetujuan subjek data sebelum data diproses oleh aplikasi.

---

## 3. Apa yang Test-nya Ajarkan (What the Test Teaches)

Unit test pada Koan 02 menguji perilaku sistem saat proses registrasi/pendaftaran akun:
1. **Penolakan Tanpa Consent (`test_registration_requires_consent`)**:
   - Memastikan bahwa jika request registrasi dikirimkan dengan parameter `consent_given = False` atau kosong, API wajib menolaknya dan mengembalikan HTTP status `400 Bad Request`.
   - Ini mengajarkan kita untuk meletakkan validasi persetujuan di pintu gerbang utama aplikasi (level API/View) sebelum data disimpan di database.
2. **Pencatatan Log Audit (`test_successful_registration_logs_consent`)**:
   - Memastikan jika registrasi sukses (`consent_given = True`), sistem secara otomatis membuat entry baru di tabel `ConsentLog`.
   - Tes memverifikasi bahwa record tersebut memuat IP address client dan versi kebijakan privasi (`policy_version`) dengan benar.

---

## 4. Kisi-Kisi (Hints)

Untuk menyelesaikan tantangan ini:
- **Validasi Input**:
  Gunakan penanganan logika standard pada Django REST Framework (DRF) view Anda. Cek payload input `request.data` untuk mendeteksi apakah `consent_given` bernilai `True`. Jika tidak, kembalikan `Response` dengan status `status.HTTP_400_BAD_REQUEST`.
- **Mendapatkan IP Address**:
  Untuk merekam IP address client di Django, Anda bisa membacanya dari header metadata request:
  `request.META.get('REMOTE_ADDR')`.
- **Konsistensi Database**:
  Karena proses ini melibatkan pembuatan akun User Django dan pencatatan Consent Log secara bersamaan, sangat disarankan untuk membungkus operasi penyimpanan ini di dalam database transaction block (`transaction.atomic`) agar terhindar dari kondisi inkonsistensi (user terbuat tapi log consent gagal dibuat).

---

## 5. Studi Kasus Berpikir Kritis (Critical Thinking Case Study)

1. *Bayangkan sebuah skenario di mana perusahaan merilis versi Kebijakan Privasi baru (misal dari v1.0 ke v1.1) karena ada fitur baru. Bagaimana sistem Anda mendeteksi pengguna lama yang belum menyetujui versi v1.1? Apakah mereka harus diblokir langsung saat login, atau diberi pop-up persetujuan saat membuka aplikasi?*
2. *Bagaimana jika pengguna menuntut bahwa mereka tidak pernah memberikan persetujuan, dan mengklaim bahwa data log di database kita dimanipulasi oleh administrator internal? Bagaimana Anda dapat membuktikan keaslian audit log tersebut dari sisi keamanan informasi (misalnya menggunakan hashing atau tanda tangan digital)?*
