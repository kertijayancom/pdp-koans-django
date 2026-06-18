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

## 3. Tingkat Kesulitan (Difficulty Levels)

Tantangan ini dibagi menjadi tiga tingkat kesulitan:

1. **[Basic] Incident Containment / Lockout (`test_01_basic_containment_locks_compromised_account`)**:
   - Memblokir akses secara instan ke endpoint sensitif jika pengguna memiliki flag `is_compromised = True` (pada atribut Python objek user) atau terdaftar di database `CompromisedUser`, kemudian mengembalikan status `423 Locked`.
2. **[Intermediate] Generator Laporan BPPA (`test_02_intermediate_bppa_report_structure_and_persistence`)**:
   - Mencari informasi insiden kebocoran data berdasarkan `incident_id` pada model `IncidentReport`.
   - Mengubah status `reported_to_bppa` menjadi `True` pada database dan mengembalikan struktur data resmi sesuai Pasal 35 ayat (1) UU PDP.
3. **[Advanced] Otomatisasi Deteksi Anomali & Containment (`test_03_advanced_automatic_threat_containment`)**:
   - Mensimulasikan deteksi ancaman otomatis. Jika request dikirim dengan parameter pemicu `?trigger_anomaly=true`, sistem harus otomatis mencatat email pengguna tersebut ke dalam tabel `CompromisedUser` dengan status `is_compromised = True` di database, dan langsung mengunci aksesnya saat itu juga serta pada request berikutnya.

---

## 4. Kisi-Kisi (Hints)

### Level Basic
- Cek apakah akun terindikasi kompromi via properti Python: `getattr(request.user, 'is_compromised', False)`.
- Cek juga di database menggunakan `CompromisedUser.objects.filter(user_email=request.user.email, is_compromised=True).exists()`.
- Jika salah satu bernilai `True`, segera kembalikan respons dengan status `status.HTTP_423_LOCKED`.

### Level Intermediate
- Cari insiden dengan `IncidentReport.objects.get(id=incident_id)`. Tangani jika tidak ditemukan (`IncidentReport.DoesNotExist`) dengan status `404 Not Found`.
- Set `incident.reported_to_bppa = True` dan simpan ke database (`incident.save()`).
- Bangun JSON output dengan format pemetaan:
  - `incident_id` -> `incident.id`
  - `incident_time` -> `incident.timestamp.isoformat()`
  - `failure_cause` -> `incident.root_cause`
  - `affected_users` -> `incident.impacted_subjects_count`
  - `mitigation_actions` -> `incident.remediation_actions`

### Level Advanced
- Di awal method `get()`, periksa jika parameter query `trigger_anomaly` bernilai `'true'`.
- Jika ya, jalankan metode upsert di database:
  `CompromisedUser.objects.update_or_create(user_email=request.user.email, defaults={"is_compromised": True})`
- Segera kembalikan respons `423 Locked` dengan pesan peringatan keamanan.

---

## 5. Studi Kasus Berpirik Kritis (Critical Thinking Case Study)

1. **Skalabilitas Deteksi Otomatis (IDS/IPS)**:
   *Dalam skenario peretasan massal, ribuan akun dapat terkompromi dalam hitungan detik. Melakukan pelabelan status `is_compromised = True` secara manual oleh administrator satu per satu sangat tidak efisien. Bagaimana cara merancang arsitektur sistem deteksi otomatis (IDS/IPS) yang terintegrasi dengan Application Performance Monitoring (APM) untuk mendeteksi anomali traffic (misalnya: lonjakan request ekspor data dari satu IP) dan langsung mengunci akun tersebut secara otomatis?*
2. **Alur Pemulihan yang Aman (Account Recovery)**:
   *Ketika sistem aplikasi dikunci sebagian (locked out) karena status kompromi, bagaimana cara kita menyediakan alur pemulihan akun (account recovery flow) yang aman bagi pengguna yang sah untuk membuktikan identitas mereka kembali tanpa membuka celah bagi peretas (misalnya melalui verifikasi multi-faktor / MFA out-of-band)?*
