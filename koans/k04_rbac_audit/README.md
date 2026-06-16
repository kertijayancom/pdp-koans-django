# Learning Notes: Koan 04 - RBAC & Access Audit Trail 🛡️

Tantangan ini berfokus pada prinsip **Pembatasan Akses (Role-Based Access Control) & Jejak Audit Kriptografi (Tamper-Resistant Audit Trail)** berdasarkan standar ISO 27001 dan regulasi UU PDP.

---

## 1. Penjelasan Konsep (Concept Explanation)

Dalam dunia keamanan informasi, ada prinsip penting yang disebut **Least Privilege** (Hak Akses Minimum):
- Pengguna sistem hanya boleh diberikan hak akses terkecil yang diperlukan untuk menyelesaikan tugas mereka.
- Kita menerapkan ini melalui **Role-Based Access Control (RBAC)**, yaitu pembatasan wewenang berdasarkan peran pengguna (misal: membedakan hak staf biasa dengan Petugas Pelindungan Data/Data Protection Officer (DPO)).

Di dalam Koan ini, tantangan dibagi ke dalam **3 tingkat kesulitan (Level)**:
1. **Level 1: Basic (Role-Based Access Control)**: Membuat DRF Permission Class kustom untuk memastikan hanya pengguna dengan peran DPO (`is_dpo = True`) yang dapat membaca data sensitif.
2. **Level 2: Intermediate (Access Audit Trail)**: Merekam log pembacaan secara otomatis ke tabel `AccessAuditLog` setiap kali DPO mengakses data.
3. **Level 3: Advanced (Cryptographic Hash Chain)**:
   - Di dunia nyata, log audit di database rawan dirusak/dihapus oleh peretas internal untuk menyembunyikan aksi pencurian data mereka (*insider threat*).
   - Kita mencegahnya dengan teknik **Hash Chain** (seperti Blockchain): Setiap record log memiliki signature hasil SHA256 dari gabungan datanya sendiri ditambah nilai signature dari record log sebelumnya (`previous_hash`).
   - Jika satu record di tengah dihapus atau dimodifikasi, rantai hash akan patah (*broken chain*) dan verifikasi integritas sistem (`verify_integrity()`) akan mendeteksi manipulasi tersebut secara instan.

---

## 2. Kenapa Penting (Why It Matters)

Mengapa kombinasi RBAC dan Audit Trail ini sangat krusial?
1. **Dampak Hukum (UU PDP Pasal 40)**: Pengendali data pribadi wajib mencegah akses data pribadi secara tidak sah. Membiarkan staf biasa (non-DPO) membaca data sensitif pelanggan tanpa filter wewenang adalah pelanggaran hukum.
2. **Kepatuhan ISO 27001 (Control A.8.2 / A.5.15 - Access Rights & Audit Logging)**: Organisasi harus merekam aktivitas operator/admin yang mengakses informasi rahasia. Log audit ini sering menjadi bukti utama yang diminta auditor saat pemeriksaan kepatuhan tahunan.
3. **Penyelidikan Forensik & Akuntabilitas**: Jika terjadi kebocoran data di dalam organisasi, log audit akses yang keasliannya terjamin (karena dilindungi rantai kriptografi) adalah satu-satunya alat bukti hukum yang sah untuk membuktikan siapa operator internal yang membocorkannya.

---

## 3. Apa yang Test-nya Ajarkan (What the Test Teaches)

Unit test pada Koan 04 menguji aspek-aspek berikut:
1. **[Basic] test_01_non_dpo_denied_access**:
   - Memastikan pengguna non-DPO ditolak dengan status `403 Forbidden` dan tidak mencatat log apa pun.
2. **[Intermediate] test_02_dpo_allowed_and_logged**:
   - Memastikan DPO diizinkan masuk (`200 OK`) dan aktivitasnya sukses tercatat di log audit.
3. **[Advanced] test_03_audit_log_hash_chain_integrity**:
   - Memverifikasi bahwa setiap kali log baru dibuat, sistem otomatis mencari log terakhir di database, memautkan `previous_hash` dengan benar, dan menghitung `hash_signature` menggunakan SHA256 secara valid.
4. **[Advanced] test_04_audit_log_tamper_detection**:
   - Memverifikasi bahwa jika kita merusak isi data log (seperti mengubah IP asal secara manual di database) atau menghapus log di tengah rantai secara ilegal, fungsi verifikasi `AccessAuditLog.verify_integrity()` akan langsung mengembalikan nilai `False`.

---

## 4. Kisi-Kisi (Hints)

Untuk menyelesaikan tantangan ini:
- **[Advanced] Menghitung Hash Signature**:
  - Impor pustaka `hashlib` bawaan Python.
  - Di dalam method `calculate_hash(self)`:
    - Buat format string: `raw_data = f"{self.operator_email}|{self.action}|{self.accessed_user_id}|{self.ip_address}|{self.previous_hash}"`
    - Lakukan hashing: `return hashlib.sha256(raw_data.encode('utf-8')).hexdigest()`.
- **[Advanced] Pembuatan Rantai di Views**:
  - Di dalam `CustomerSensitiveDataView`, sebelum menyimpan `AccessAuditLog`:
    - Cari entri log terakhir: `last_log = AccessAuditLog.objects.all().order_by('-id').first()`.
    - Jika ada, set `prev_hash = last_log.hash_signature`. Jika tidak, set `prev_hash = ""`.
    - Inisialisasi objek log: `log = AccessAuditLog(..., previous_hash=prev_hash)`.
    - Hitung signature: `log.hash_signature = log.calculate_hash()`, kemudian panggil `log.save()`.
- **[Advanced] Verifikasi Rantai**:
  - Di dalam staticmethod `verify_integrity()`:
    - Ambil semua log terurut `id`: `logs = AccessAuditLog.objects.all().order_by('id')`.
    - Lakukan loop. Untuk index `0`, pastikan `previous_hash` kosong. Untuk index `i`, pastikan `previous_hash` cocok dengan `hash_signature` index `i-1`.
    - Pastikan hasil `log.calculate_hash()` di setiap baris selalu cocok dengan `hash_signature` yang tersimpan.

---

## 5. Studi Kasus Berpikir Kritis (Critical Thinking Case Study)

1. *Meskipun kita menggunakan Cryptographic Hash Chain, penyerang yang memiliki akses database penuh masih bisa melakukan kecurangan dengan cara memodifikasi data log lalu menghitung ulang (re-calculate) semua signature berikutnya dari awal hingga akhir sehingga rantainya terlihat tetap valid. Bagaimana cara Anda mencegah serangan penulisan ulang rantai log ini (misalnya menggunakan skema tanda tangan digital asimetris/RSA dengan private key yang disimpan aman di HSM/KMS)?*
2. *Dalam sistem microservices skala besar dengan jutaan transaksi per menit, menulis log akses langsung ke database relasional utama (PostgreSQL) pada setiap request baca dapat membebani database (bottleneck). Bagaimana Anda mendesain arsitektur pengumpulan log audit yang efisien dan tidak mengganggu kinerja sistem utama (misal menggunakan Message Queue seperti Kafka/RabbitMQ)?*
