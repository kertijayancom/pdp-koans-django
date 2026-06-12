# Learning Notes: Koan 04 - RBAC & Access Audit Trail 🛡️

Tantangan ini berfokus pada prinsip **Pembatasan Akses (Role-Based Access Control) & Perekaman Jejak Audit (Access Audit Trail)** berdasarkan standar ISO 27001 dan regulasi UU PDP.

---

## 1. Penjelasan Konsep (Concept Explanation)

Dalam dunia keamanan informasi, ada prinsip penting yang disebut **Least Privilege** (Hak Akses Minimum):
- Pengguna sistem hanya boleh diberikan hak akses terkecil yang diperlukan untuk menyelesaikan tugas mereka.
- Kita menerapkan ini melalui **Role-Based Access Control (RBAC)**, yaitu pembatasan wewenang berdasarkan peran pengguna (misal: membedakan hak staf biasa dengan Petugas Pelindungan Data/Data Protection Officer (DPO)).

Selain membatasi akses, setiap kali data pribadi yang bersifat sensitif diakses oleh siapa pun, sistem wajib merekam kejadian tersebut ke dalam **Access Audit Trail** (Log Audit Akses):
- Log ini harus disimpan secara independen di database.
- Log mencatat informasi penting: *Siapa* yang mengakses (operator email), *data siapa* yang dibaca (customer ID), *kapan* diakses (timestamp), dan *dari mana* akses dilakukan (IP address).

---

## 2. Kenapa Penting (Why It Matters)

Mengapa kombinasi RBAC dan Audit Trail ini sangat krusial?
1. **Dampak Hukum (UU PDP Pasal 40)**: Pengendali data pribadi wajib mencegah akses data pribadi secara tidak sah. Membiarkan staf biasa (non-DPO) membaca data sensitif pelanggan tanpa filter wewenang adalah pelanggaran hukum.
2. **Kepatuhan ISO 27001 (Control A.8.2 / A.5.15 - Access Rights & Audit Logging)**: Organisasi harus merekam aktivitas operator/admin yang mengakses informasi rahasia. Log audit ini sering menjadi bukti utama yang diminta auditor saat pemeriksaan kepatuhan tahunan.
3. **Penyelidikan Forensik**: Jika terjadi kebocoran data di dalam organisasi (*insider threat*), log audit akses adalah satu-satunya cara bagi tim keamanan untuk melacak siapa operator internal yang telah membaca atau menyalin data tersebut secara tidak wajar.

---

## 3. Apa yang Test-nya Ajarkan (What the Test Teaches)

Unit test pada Koan 04 menguji dua pilar keamanan akses:
1. **Verifikasi Wewenang Peran (`test_non_dpo_access_forbidden`)**:
   - Memastikan bahwa pengguna terautentikasi yang *tidak* memiliki flag `is_dpo = True` ditolak aksesnya (mengembalikan status `403 Forbidden`) saat mencoba mengakses endpoint data pelanggan sensitif.
   - Ini mengajarkan kita pentingnya merancang lapisan keamanan berbasis izin (*permission classes*) di tingkat API.
2. **Perekaman Otomatis Log Akses (`test_dpo_access_logs_audit_trail`)**:
   - Memastikan bahwa saat pengguna dengan peran DPO berhasil mengakses data, sistem secara otomatis menyimpan record baru di tabel `AccessAuditLog`.
   - Ini mendisiplinkan pengembang untuk meletakkan logika penulisan log audit pada siklus hidup request-response API yang berhasil.

---

## 4. Kisi-Kisi (Hints)

Untuk menyelesaikan tantangan ini:
- **Permission Class di DRF**:
  Tulis kelas kustom di `views.py` yang mewarisi `BasePermission` dari Django REST Framework. Implementasikan metode `has_permission(self, request, view)` untuk memverifikasi apakah `request.user` terautentikasi dan memiliki atribut `is_dpo` bernilai `True`.
- **Memicu Log Audit Secara Otomatis**:
  Log audit akses sebaiknya dibuat di dalam metode penanganan request API yang berhasil (seperti `get()` atau `retrieve()`).
  - Dapatkan operator email dari `request.user.email`.
  - Dapatkan target customer ID dari argumen URL/query (misal: `kwargs.get('id')`).
  - Dapatkan IP address client menggunakan `request.META.get('REMOTE_ADDR')`.
  - Simpan menggunakan ORM: `AccessAuditLog.objects.create(...)`.

---

## 5. Studi Kasus Berpikir Kritis (Critical Thinking Case Study)

1. *Bagaimana jika database log audit akses (`AccessAuditLog`) diserang oleh peretas internal yang memiliki akses database penuh, lalu mereka menghapus baris log tertentu untuk menghilangkan jejak kejahatan mereka? Strategi apa yang bisa diterapkan untuk menjaga integritas log audit agar tidak bisa diubah atau dihapus (misal menggunakan Write Once Read Many (WORM) storage, pengiriman log secara real-time ke SIEM eksternal, atau teknik cryptographic hashing)?*
2. *Dalam sistem microservices skala besar dengan jutaan transaksi per menit, menulis log akses langsung ke database relasional utama (PostgreSQL) pada setiap request baca dapat membebani database (bottleneck). Bagaimana Anda mendesain arsitektur pengumpulan log audit yang efisien dan tidak mengganggu kinerja sistem utama (misal menggunakan Message Queue seperti Kafka/RabbitMQ)?*
