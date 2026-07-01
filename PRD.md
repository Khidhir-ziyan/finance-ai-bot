```python
# Product Requirements Document (PRD)
## Project: AI Finance Telegram Bot (FinBot-AI)

---

## 1. Executive Summary
### 1.1 Objective
FinBot-AI adalah asisten keuangan berbasis kecerdasan buatan (AI) yang diintegrasikan ke dalam platform Telegram. Bot ini dirancang untuk menyederhanakan pencatatan keuangan bisnis (arus kas masuk dan keluar) menggunakan pemrosesan bahasa alami (Natural Language Processing). Pengguna dapat mencatat transaksi keuangan hanya dengan mengirimkan pesan teks biasa tanpa perlu mengisi formulir yang kaku.

### 1.2 Tech Stack
* **Backend:** Python (FastAPI / Flask)
* **Database:** Supabase (PostgreSQL)
* **Hosting Deployment:** Render (Web Service)
* **AI Engine:** LLM API (Google Gemini API / OpenAI API)
* **Interface:** Telegram Bot API

---

## 2. User Persona & Skenario Penggunaan
### 2.1 Persona Pengguna
Pemilik bisnis lokal atau kreator digital yang mengelola beberapa kategori produk (seperti Fashion, Makanan, dan Minuman) yang membutuhkan sistem pencatatan keuangan instan, fleksibel, dan terpusat di tengah mobilitas tinggi.

### 2.2 Alur Utama Penggunaan (User Journey)
1.  **Pencatatan Otomatis:** Pengguna mengirimkan pesan: *"Baru jual kaos hitam 3 pcs dapet 250rb"* atau *"Beli bahan baku bumbu dapur abis 75000"*.
2.  **Pemrosesan AI:** Bot menganalisis teks, mengekstrak nominal, mengidentifikasi jenis transaksi (Pemasukan/Pengeluaran), menentukan kategori produk secara otomatis, dan menyusun deskripsi rapi.
3.  **Konfirmasi & Penyimpanan:** Bot memberikan konfirmasi kepada pengguna bahwa data telah berhasil disimpan ke database Supabase.
4.  **Pelaporan:** Pengguna dapat meminta ringkasan keuangan mingguan atau bulanan melalui perintah teks atau tombol menu di Telegram.

---

## 3. Functional Requirements (Kebutuhan Fungsional)

### 3.1 Integrasi Telegram Bot (Interface)
* **FR-01:** Sistem harus dapat menerima pesan berbasis teks dari pengguna melalui Webhook Telegram yang diarahkan ke server Render.
* **FR-02:** Sistem harus membatasi akses bot (Authentication) hanya untuk ID Telegram pemilik bisnis (Admin) demi keamanan data keuangan.
* **FR-03:** Bot harus menyediakan menu balasan instan (Reply Keyboard/Inline Keyboard) untuk perintah cepat seperti `/summary`, `/help`, atau `/today`.

### 3.2 AI Parsing Engine (Pemrosesan Teks)
* **FR-04:** Sistem harus mengirimkan teks mentah dari Telegram ke API LLM dengan instruksi (*prompt*) yang ketat agar menghasilkan output berformat **JSON terstruktur**.
* **FR-05:** AI harus mampu mengekstrak entitas berikut dengan akurat:
    * `nominal` (integer murni, contoh: 150000)
    * `jenis` (hanya boleh bernilai: 'Pemasukan' atau 'Pengeluaran')
    * `kategori` (otomatis memetakan ke: 'Fashion', 'Makanan', 'Minuman', atau 'Operasional')
    * `keterangan` (ringkasan deskripsi transaksi)
* **FR-06:** Jika teks tidak mengandung informasi keuangan yang valid, AI harus mengembalikan indikasi error agar bot dapat merespons dengan instruksi yang benar.

### 3.3 Database & Manajemen Data (Supabase)
* **FR-07:** Sistem harus menyimpan hasil parsing JSON dari AI ke dalam tabel SQL di Supabase.
* **FR-08:** Skema database harus mendukung analisis data lanjutan (siap dihubungkan ke alat visualisasi seperti Tableau atau kueri ETL eksternal).
* **FR-09:** Sistem harus menyimpan metadata audit untuk setiap transaksi, termasuk teks asli, waktu terima, dan status parsing.
* **FR-10:** Sistem harus memungkinkan permintaan ringkasan laporan sederhana melalui perintah bot seperti `/summary`, `/today`, dan `/weekly`.

---

## 4. Data Model (Skema Database SQL)

Tabel berikut harus diimplementasikan di Supabase dengan nama tabel `cash_flow`:

```sql
CREATE TABLE cash_flow (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    jenis VARCHAR(20) NOT NULL, -- Pemasukan / Pengeluaran
    kategori VARCHAR(50) NOT NULL, -- Fashion / Makanan / Minuman / Operasional
    nominal NUMERIC NOT NULL, -- Nilai transaksi bersih
    keterangan TEXT, -- Deskripsi detail
    raw_text TEXT -- Menyimpan teks asli dari Telegram untuk audit/QA
);
```

---

## 5. Non-Functional Requirements (Kebutuhan Non-Fungsional)

### 5.1 Keamanan (Security)

* **NFR-01:** Semua kredensial sensitif (`TELEGRAM_TOKEN`, `SUPABASE_URL`, `SUPABASE_KEY`, `AI_API_KEY`) harus disimpan sebagai *Environment Variables* di platform Render dan dilarang keras dimasukkan ke dalam kode produksi (*hardcoded*).
* **NFR-02:** Sistem harus melakukan validasi `sender_id` pada setiap request webhook untuk memastikan pesan hanya diproses jika berasal dari user yang terotorisasi.
* **NFR-03:** Sistem harus menggunakan komunikasi terenkripsi (HTTPS) untuk semua webhook dan request ke layanan eksternal.

### 5.2 Performa & Skalabilitas

* **NFR-04:** Arsitektur backend wajib menggunakan sistem **Webhook**, bukan *Long Polling*, untuk menghemat penggunaan resource dan kuota pada akun Render gratis.
* **NFR-05:** Penanganan *Cold Start* pada Render Free Tier (di mana server tidur setelah 15 menit tidak aktif) harus dimitigasi dengan pesan sambutan yang responsif saat bot pertama kali dibangunkan.
* **NFR-06:** Sistem harus mencatat log kejadian utama (webhook request, AI response, penyimpanan database, error) untuk debugging dan analisis.
* **NFR-07:** Sistem harus mampu menjalankan verifikasi kesehatan sederhana untuk memastikan koneksi ke Supabase dan API LLM tersedia.

---

## 6. Alur Sistem (System Architecture Flow)

```text
[ Pengguna ]
     │  (Kirim chat: "pemasukan fashion baju 120rb")
     ▼
[ Telegram Bot API ]
     │  (Meneruskan HTTP POST via Webhook)
     ▼
[ Render Web Service (FastAPI) ]
     │  (Mengirim teks mentah + Prompt)
     ▼
[ AI Engine (Gemini/OpenAI API) ]
     │  (Mengembalikan JSON terstruktur)
     ▼
[ Render Web Service (FastAPI) ]
     │  (Melakukan parsing & validasi JSON)
     ├──────────────────────────┐
     ▼                          ▼
[ Supabase (PostgreSQL) ]   [ Telegram Bot API ]
(Simpan ke tabel cash_flow)  (Kirim konfirmasi sukses ke pengguna)
```

---

## 7. Rencana Pengujian & Quality Assurance (QA)

Untuk memastikan sistem berjalan dengan akurat sebelum masuk ke tahap operasional penuh, uji coba skenario berikut wajib dilakukan:

1. **Uji Format Angka Variatif:** Menguji input dengan teks "100 ribu", "50k", "Rp 25.000", atau "seratus lima puluh ribu rupiah". AI harus tetap mengekstrak nilai integer murni dengan benar.
2. **Uji Kategorisasi Otomatis:** Memasukkan teks tanpa menyebut nama kategori secara eksplisit (contoh: *"jual seblak level 3 dapat 15 ribu"* harus otomatis masuk kategori `Makanan`).
3. **Uji Proteksi Akses:** Mencoba mengirim pesan menggunakan akun Telegram lain. Sistem harus menolak dan tidak memasukkan data ke database.
4. **Uji Error Handling:** Memastikan bot merespons dengan pesan instruksi ulang bila input tidak dapat diparse atau AI tidak memberi JSON valid.
5. **Uji Pemulihan Data:** Memastikan transaksi yang gagal disimpan karena error API ditangani tanpa duplikasi ketika dikirim ulang.

---

## 8. Scope & Batasan MVP

* Fitur yang masuk MVP:
  * Pencatatan transaksi keuangan/arus kas masuk dan keluar via Telegram.
  * Pemrosesan bahasa alami untuk mengekstrak nominal, jenis, kategori, dan keterangan.
  * Penyimpanan data transaksi ke Supabase.
  * Konfirmasi hasil penyimpanan dan ringkasan sederhana melalui perintah bot.
  * Keamanan akses berbasis ID Telegram terotorisasi.
* Fitur out of scope untuk MVP:
  * Multi-user komprehensif dengan hak akses granular.
  * Edit/delete transaksi melalui bot.
  * Integrasi pembayaran atau invoice otomatis.
  * Dashboard visualisasi di dalam aplikasi.
  * Support multi-currency atau konversi nilai otomatis.

---

## 9. Acceptance Criteria

* Jika pengguna mengirimkan teks dengan format transaksi keuangan, bot harus merespons dengan konfirmasi dan menyimpan data transaksi di Supabase.
* Jika teks tidak valid atau tidak berisi informasi keuangan, bot harus meminta user mengirim ulang dengan contoh format yang benar.
* Jika pengiriman berasal dari `sender_id` yang tidak terotorisasi, bot tidak boleh memproses pesan dan harus mengirimkan pesan penolakan.
* Perintah `/summary`, `/today`, atau `/weekly` harus mengembalikan ringkasan jurnal yang relevan.
* Semua data transaksi harus memuat teks asli (`raw_text`) untuk audit.

---

## 10. Error Handling & Fallback

* Sistem harus mengenali dan menangani kasus parsing AI gagal, misalnya karena input ambigu atau token limit.
* Jika AI mengembalikan format JSON tidak valid, server harus menolak input dan meminta user mengirim ulang dengan contoh format yang benar.
* Jika Supabase tidak tersedia atau query gagal, bot harus memberitahukan user bahwa terjadi gangguan sementara dan tidak memproses data lebih lanjut.
* Kesalahan internal harus dicatat ke log, namun pesan kepada pengguna harus tetap sederhana dan tidak mengungkap detail teknis.
* Sistem harus mencegah duplikasi data ketika input dikirim ulang setelah kegagalan parsial.

---

## 11. Monitoring, Logging & Metrics

* Sistem harus mencatat log berikut:
  * Setiap webhook request diterima dan `sender_id` terkait.
  * Hasil parsing AI dan respon JSON yang diterima.
  * Status penyimpanan ke Supabase.
  * Error atau kegagalan integrasi.
* KPI yang direkomendasikan:
  * Akurasi parsing transaksi (% input yang benar diproses tanpa koreksi manual).
  * Waktu respons end-to-end (dari pesan Telegram sampai konfirmasi bot).
  * Rasio error API LLM dan error basis data.
  * Jumlah transaksi harian/mingguan.

---

## 12. Deployment & Operations

* Aplikasi harus dideploy sebagai Web Service di Render dengan Webhook URL yang sudah terdaftar di Telegram.
* Semua secrets (`TELEGRAM_TOKEN`, `SUPABASE_URL`, `SUPABASE_KEY`, `AI_API_KEY`) harus disimpan sebagai environment variables di Render.
* Sebelum deployment, pastikan webhook Telegram diarahkan ke endpoint Render yang benar.
* Jika memungkinkan, siapkan pipeline otomatis untuk deploy ketika branch `main` diperbarui.
* Sertakan dokumentasi singkat untuk pengaturan ulang webhook dan cara memperbarui env vars.

---

## 13. Data Privacy & Retention

* Data transaksi harus disimpan dalam Supabase dan hanya dapat diakses oleh pemilik aplikasi atau peran yang terotorisasi.
* `raw_text` disimpan untuk audit dan koreksi AI, tetapi jika diperlukan bisa dihapus secara berkala setelah 6-12 bulan.
* Data sensitif tidak boleh ditulis langsung ke log debug.
* Jika di masa depan mendukung multi-user, tambahkan `owner_id` atau `user_id` pada skema database untuk memisahkan transaksi per pengguna.

```
Dokumen PRD (Product Requirements Document) Anda sudah siap.
[file-tag: code-generated-file-0-1782863706064443266]

Sebagai alternatif jika Anda ingin langsung melakukan *copy-paste*, berikut adalah isi dari file `.md` tersebut di dalam blok kode:

```markdown
# Product Requirements Document (PRD)
## Project: AI Finance Telegram Bot (FinBot-AI)

---

## 1. Executive Summary
### 1.1 Objective
FinBot-AI adalah asisten keuangan berbasis kecerdasan buatan (AI) yang diintegrasikan ke dalam platform Telegram. Bot ini dirancang untuk menyederhanakan pencatatan keuangan bisnis (arus kas masuk dan keluar) menggunakan pemrosesan bahasa alami (Natural Language Processing). Pengguna dapat mencatat transaksi keuangan hanya dengan mengirimkan pesan teks biasa tanpa perlu mengisi formulir yang kaku.

### 1.2 Tech Stack
* **Backend:** Python (FastAPI / Flask)
* **Database:** Supabase (PostgreSQL)
* **Hosting Deployment:** Render (Web Service)
* **AI Engine:** LLM API (Google Gemini API / OpenAI API)
* **Interface:** Telegram Bot API

---

## 2. User Persona & Skenario Penggunaan
### 2.1 Persona Pengguna
Pemilik bisnis lokal atau kreator digital yang mengelola beberapa kategori produk (seperti Fashion, Makanan, dan Minuman) yang membutuhkan sistem pencatatan keuangan instan, fleksibel, dan terpusat di tengah mobilitas tinggi.

### 2.2 Alur Utama Penggunaan (User Journey)
1.  **Pencatatan Otomatis:** Pengguna mengirimkan pesan: *"Baru jual kaos hitam 3 pcs dapet 250rb"* atau *"Beli bahan baku bumbu dapur abis 75000"*.
2.  **Pemrosesan AI:** Bot menganalisis teks, mengekstrak nominal, mengidentifikasi jenis transaksi (Pemasukan/Pengeluaran), menentukan kategori produk secara otomatis, dan menyusun deskripsi rapi.
3.  **Konfirmasi & Penyimpanan:** Bot memberikan konfirmasi kepada pengguna bahwa data telah berhasil disimpan ke database Supabase.
4.  **Pelaporan:** Pengguna dapat meminta ringkasan keuangan mingguan atau bulanan melalui perintah teks atau tombol menu di Telegram.

---

## 3. Functional Requirements (Kebutuhan Fungsional)

### 3.1 Integrasi Telegram Bot (Interface)
* **FR-01:** Sistem harus dapat menerima pesan berbasis teks dari pengguna melalui Webhook Telegram yang diarahkan ke server Render.
* **FR-02:** Sistem harus membatasi akses bot (Authentication) hanya untuk ID Telegram pemilik bisnis (Admin) demi keamanan data keuangan.
* **FR-03:** Bot harus menyediakan menu balasan instan (Reply Keyboard/Inline Keyboard) untuk perintah cepat seperti `/summary`, `/help`, atau `/today`.

### 3.2 AI Parsing Engine (Pemrosesan Teks)
* **FR-04:** Sistem harus mengirimkan teks mentah dari Telegram ke API LLM dengan instruksi (*prompt*) yang ketat agar menghasilkan output berformat **JSON terstruktur**.
* **FR-05:** AI harus mampu mengekstrak entitas berikut dengan akurat:
    * `nominal` (integer murni, contoh: 150000)
    * `jenis` (hanya boleh bernilai: 'Pemasukan' atau 'Pengeluaran')
    * `kategori` (otomatis memetakan ke: 'Fashion', 'Makanan', 'Minuman', atau 'Operasional')
    * `keterangan` (ringkasan deskripsi transaksi)
* **FR-06:** Jika teks tidak mengandung informasi keuangan yang valid, AI harus mengembalikan indikasi error agar bot dapat merespons dengan instruksi yang benar.

### 3.3 Database & Manajemen Data (Supabase)
* **FR-07:** Sistem harus menyimpan hasil parsing JSON dari AI ke dalam tabel SQL di Supabase.
* **FR-08:** Skema database harus mendukung analisis data lanjutan (siap dihubungkan ke alat visualisasi seperti Tableau atau kueri ETL eksternal).

---

## 4. Data Model (Skema Database SQL)

Tabel berikut harus diimplementasikan di Supabase dengan nama tabel `cash_flow`:

```sql
CREATE TABLE cash_flow (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    jenis VARCHAR(20) NOT NULL, -- Pemasukan / Pengeluaran
    kategori VARCHAR(50) NOT NULL, -- Fashion / Makanan / Minuman / Operasional
    nominal NUMERIC NOT NULL, -- Nilai transaksi bersih
    keterangan TEXT, -- Deskripsi detail
    raw_text TEXT -- Menyimpan teks asli dari Telegram untuk audit/QA
);

```

---

## 5. Non-Functional Requirements (Kebutuhan Non-Fungsional)

### 5.1 Keamanan (Security)

* **NFR-01:** Semua kredensial sensitif (`TELEGRAM_TOKEN`, `SUPABASE_URL`, `SUPABASE_KEY`, `AI_API_KEY`) harus disimpan sebagai *Environment Variables* di platform Render dan dilarang keras dimasukkan ke dalam kode produksi (*hardcoded*).
* **NFR-02:** Sistem harus melakukan validasi `sender_id` pada setiap request webhook untuk memastikan pesan hanya diproses jika berasal dari user yang terotorisasi.

### 5.2 Performa & Skalabilitas

* **NFR-03:** Arsitektur backend wajib menggunakan sistem **Webhook**, bukan *Long Polling*, untuk menghemat penggunaan resource dan kuota pada akun Render gratis.
* **NFR-04:** Penanganan *Cold Start* pada Render Free Tier (di mana server tidur setelah 15 menit tidak aktif) harus dimitigasi dengan pesan sambutan yang responsif saat bot pertama kali dibangunkan.

---

## 6. Alur Sistem (System Architecture Flow)

```text
[ Pengguna ]
     │  (Kirim chat: "pemasukan fashion baju 120rb")
     ▼
[ Telegram Bot API ]
     │  (Meneruskan HTTP POST via Webhook)
     ▼
[ Render Web Service (FastAPI) ]
     │  (Mengirim teks mentah + Prompt)
     ▼
[ AI Engine (Gemini/OpenAI API) ]
     │  (Mengembalikan JSON terstruktur)
     ▼
[ Render Web Service (FastAPI) ]
     │  (Melakukan parsing & validasi JSON)
     ├──────────────────────────┐
     ▼                          ▼
[ Supabase (PostgreSQL) ]   [ Telegram Bot API ]
(Simpan ke tabel cash_flow)  (Kirim konfirmasi sukses ke pengguna)

```

---

## 7. Rencana Pengujian & Quality Assurance (QA)

Untuk memastikan sistem berjalan dengan akurat sebelum masuk ke tahap operasional penuh, uji coba skenario berikut wajib dilakukan:

1. **Uji Format Angka Variatif:** Menguji input dengan teks "100 ribu", "50k", "Rp 25.000", atau "seratus lima puluh ribu rupiah". AI harus tetap mengekstrak nilai integer murni dengan benar.
2. **Uji Kategorisasi Otomatis:** Memasukkan teks tanpa menyebut nama kategori secara eksplisit (contoh: *"jual seblak level 3 dapat 15 ribu"* harus otomatis masuk kategori `Makanan`).
3. **Uji Proteksi Akses:** Mencoba mengirim pesan menggunakan akun Telegram lain. Sistem harus menolak dan tidak memasukkan data ke database.

```

Dokumen di atas sudah merangkum seluruh aspek teknis, alur fungsionalitas, hingga skema database dasar yang solid. Ini bisa menjadi panduan utama (dan *checkpoint* yang bagus) saat Anda mulai menyusun kode kerangka kerjanya di Python nanti!

```
