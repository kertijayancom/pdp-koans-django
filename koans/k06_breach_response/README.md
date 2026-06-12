# Learning Notes: Koan 06 - Data Breach Response & Incident Containment 🛡️

Tantangan ini berfokus pada prinsip **Penanganan Insiden Keamanan & Notifikasi Kegagalan Data Pribadi (Data Breach Response)** berdasarkan regulasi UU PDP dan standar ISO 27001.

---

## 1. Penjelasan Konsep (Concept Explanation)

Ketika terjadi insiden kegagalan pelindungan data pribadi (kebocoran data), organisasi Anda dituntut untuk melakukan dua langkah cepat:
1. **Isolasi Dampak Insiden (Incident Containment)**:
   - Mengambil tindakan cepat untuk meminimalkan dampak peretasan. Salah satu langkah paling efektif adalah mengisolasi akun yang diduga terkompromi.
   - Akun yang ditandai sebagai `is_compromised = True` harus ditolak saat mencoba mengakses sumber daya sensitif demi mencegah pencurian data lebih lanjut (kembalikan HTTP `423 Locked`).
2. **Pelaporan Resmi (Notification Requirement)**:
   - Pengendali data pribadi wajib mengirimkan laporan resmi tertulis kepada subjek data pribadi dan Lembaga Pelindungan Data Pribadi (BPPA) jika terjadi kegagalan sistem.
   - Laporan ini memiliki format informasi minimum yang wajib dipenuhi: detail data yang bocor, kapan dan bagaimana kebocoran terjadi, serta upaya penanganan dan pemulihan yang sedang dilakukan.

---

## 2. Kenapa Penting (Why It Matters)

Aspek penanganan insiden dan pelaporan cepat ini sangat krusial karena:
1. **Dampak Hukum Batas Waktu 72 Jam (UU PDP Pasal 35)**: Pengendali Data Pribadi wajib menyampaikan pemberitahuan secara tertulis dalam waktu paling lambat **3 x 24 jam (72 jam)** sejak kegagalan tersebut terdeteksi. Keterlambatan pelaporan dapat berujung sanksi administratif berat.
2. **Kepatuhan ISO 27001 (Control A.5.24 - Info Security Incident Management)**: Kebijakan keamanan informasi mensyaratkan adanya prosedur terdokumentasi untuk mengidentifikasi, mengisolasi, melaporkan, dan menganalisis insiden keamanan secara cepat dan konsisten.
3. **Mencegah Kerusakan Reputasi Lebih Lanjut**: Reaksi lambat dalam memblokir akses akun yang diretas akan membiarkan penyerang mengeksploitasi data sensitif lebih lama, memperluas cakupan kerusakan (*blast radius*).

---

## 3. Apa yang Test-nya Ajarkan (What the Test Teaches)

Unit test pada Koan 06 menguji kesiapan mitigasi insiden pada aplikasi Anda:
1. **Verifikasi Isolasi Sumber Daya (`test_compromised_user_blocked`)**:
   - Memastikan pengguna yang memiliki flag `is_compromised = True` diblokir aksesnya dari API sensitif dan menerima HTTP status `423 Locked`.
   - Ini melatih pengembang untuk menaruh filter status akun di tingkat *middleware* atau *permission classes* untuk melumpuhkan akun bermasalah secara instan.
2. **Kesesuaian Format Laporan Hukum (`test_breach_notification_report_generation`)**:
   - Memverifikasi generator laporan menghasilkan format JSON dengan informasi wajib: `data_breached_details`, `incident_timestamp`, dan `mitigation_steps_taken`.

---

## 4. Kisi-Kisi (Hints)

Untuk menyelesaikan tantangan ini:
- **Lockout Logika (Containment)**:
  Tulis logika pemeriksaan di *view* atau *permission class* Anda. Jika `request.user.is_compromised` bernilai `True`, segera hentikan eksekusi dan kembalikan `Response(status=status.HTTP_423_LOCKED)`.
- **Generator Laporan**:
  Gunakan model `BreachIncident` (atau representasi insiden di database) untuk menyusun payload JSON yang komprehensif. Pastikan seluruh field wajib Pasal 35 UU PDP terisi sebelum mengembalikan data dengan status `200 OK`.

---

## 5. Studi Kasus Berpikir Kritis (Critical Thinking Case Study)

1. *Dalam skenario peretasan massal, ribuan akun dapat terkompromi dalam hitungan detik. Melakukan pelabelan status `is_compromised = True` secara manual oleh administrator satu per satu sangat tidak efisien. Bagaimana cara merancang arsitektur sistem deteksi otomatis (IDS/IPS) yang terintegrasi dengan Application Performance Monitoring (APM) untuk mendeteksi anomali traffic (misalnya: lonjakan request ekspor data dari satu IP) dan langsung mengunci akun tersebut secara otomatis?*
2. *Ketika sistem aplikasi dikunci sebagian (locked out) karena status kompromi, bagaimana cara kita menyediakan alur pemulihan akun (account recovery flow) yang aman bagi pengguna yang sah untuk membuktikan identitas mereka kembali tanpa membuka celah bagi peretas (misalnya melalui verifikasi multi-faktor / MFA out-of-band)?*
