# Peta Kepatuhan UU PDP & ISO 27001 🗺️

Dokumen ini memetakan bagaimana tantangan teknis di dalam **PDP Koans (Django Edition)** terhubung langsung dengan aspek hukum **Undang-Undang Pelindungan Data Pribadi (UU PDP)** serta kontrol standar keamanan **ISO 27001**.

---

## 📋 Tabel Cakupan Kepatuhan

| Tantangan Koans | Aspek Hukum (UU PDP) | Kontrol Standar (ISO 27001) | Detail Bahasan Teknis yang Diimplementasikan |
| :--- | :--- | :--- | :--- |
| **Koan 01: Data Minimisation**<br>`koans/k01_data_minimization/` | **Pasal 16 UU PDP**:<br>Batasan pemrosesan data | **Control A.8.11**:<br>Data masking & pembatasan akses | **Prinsip Minimisasi Data & Masking**:<br>Menghapus field tidak relevan untuk mengurangi risiko kebocoran, serta merancang fungsi penyamaran data sensitif (masking) sebelum disajikan ke user/log. |
| **Koan 02: Explicit Consent**<br>`koans/k02_explicit_consent/` | **Pasal 20 & 21 UU PDP**:<br>Persetujuan tertulis/terekam | **Control A.5.15**:<br>Manajemen hak akses & persetujuan | **Dasar Pemrosesan & Bukti Persetujuan**:<br>Memvalidasi persetujuan pengguna secara eksplisit sebelum memproses data, serta menyimpan riwayat persetujuan (Consent Log) lengkap dengan IP address dan timestamp sebagai bukti audit kepatuhan hukum. |
| **Koan 03: Data Security**<br>`koans/k03_data_security/` | **Pasal 39 UU PDP**:<br>Kewajiban menjaga keamanan data | **Control A.8.24**:<br>Penggunaan kriptografi (Enkripsi *at-rest*) | **Keamanan Data & Kriptografi**:<br>Menerjemahkan kontrol ISO 27001 terkait kriptografi ke tingkat kode dengan merancang bidang kustom terenkripsi (*EncryptedCharField*) menggunakan algoritma AES (Fernet) untuk mengamankan data sensitif (NIK) di dalam database. |
| **Koan 04: RBAC & Access Audit Trail**<br>`koans/k04_rbac_audit/` | **Pasal 40 UU PDP**:<br>Aturan pembatasan akses data | **Control A.8.2 / A.5.15**:<br>Hak akses & perekaman log audit | **Role-Based Access Control & Log Audit**:<br>Membatasi wewenang pembacaan data pribadi hanya untuk peran DPO menggunakan permission class DRF, dan mencatat histori akses operator (email, ID pelanggan, IP) untuk keperluan audit. |
| **Koan 05: Data Portability**<br>`koans/k05_data_portability/` | **Pasal 7 & 13 UU PDP**:<br>Hak pemindahan data (portabilitas) | **Control A.5.15**:<br>Manajemen permintaan subjek data | **Portabilitas Data & Proteksi IDOR**:<br>Menyediakan ekspor data pribadi dalam format JSON terstruktur untuk pengguna, serta menerapkan pemeriksaan wewenang ketat guna mencegah celah keamanan BOLA/IDOR. |
| **Koan 06: Data Breach Response**<br>`koans/k06_breach_response/` | **Pasal 35 UU PDP**:<br>Notifikasi kegagalan data pribadi | **Control A.5.24**:<br>Manajemen insiden keamanan informasi | **Isolasi Akun & Laporan BPPA**:<br>Mendeteksi dan memblokir otomatis akun yang terkompromi (isolasi insiden), serta merancang draf laporan resmi BPPA yang memenuhi ketentuan Pasal 35. |
