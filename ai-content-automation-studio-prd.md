# Product Requirements Document: AI Content Automation Studio

## Overview

AI Content Automation Studio adalah internal tool self-hosted untuk produksi dan distribusi konten pribadi yang mengotomatisasi alur kerja dari ide, brief, drafting, review, approval, scheduling, hingga autopost ke beberapa channel.[cite:118][cite:121][cite:140] Produk ini ditujukan untuk penggunaan production pribadi, berjalan di VPS self-hosted, dengan fokus utama pada efisiensi workflow konten dan kontrol penuh atas data, provider AI, serta proses publishing.[cite:19][cite:20][cite:129]

Produk ini mendukung output multi-format, termasuk YouTube Shorts, YouTube long-form, TikTok short video, artikel blog, dan caption postingan untuk X.[cite:144][cite:148] Sistem juga menambahkan integrasi OAuth 2.0 untuk YouTube autopost hingga scheduled publish, serta perluasan integrasi platform untuk TikTok dan X sebagai target publish berikutnya.[cite:144][cite:145][cite:148]

## Product Goals

Tujuan utama produk ini adalah mengurangi pekerjaan manual dalam produksi konten dengan membuat satu workflow terpusat untuk perencanaan, pembuatan, persetujuan, penjadwalan, dan publikasi konten.[cite:118][cite:121] Karena produk dipakai sebagai internal tool pribadi, prioritasnya adalah kecepatan kerja, reliabilitas workflow, fleksibilitas multi-provider AI, dan kemudahan observasi hasil publish.[cite:20][cite:129][cite:140]

Tujuan produk:
- Mengurangi waktu dari ide ke publish melalui workflow otomatis bertahap.[cite:121][cite:140]
- Menjaga konsistensi gaya konten melalui style guide dan CTA pattern memory.[cite:121][cite:124]
- Menyediakan scheduled publishing lintas platform dari satu dashboard.[cite:127][cite:144]
- Menyediakan analytics dasar pada MVP untuk memantau hasil operasional publish.[cite:136][cite:138]
- Memungkinkan kontrol penuh di lingkungan VPS self-hosted dengan username/password auth sederhana.[cite:20][cite:129]

## Users and Scope

Pengguna produk ini adalah satu orang, yaitu pemilik tool itu sendiri, sehingga sistem tidak memerlukan multi-tenant complexity atau permission matrix yang besar.[cite:20] Meskipun single-user, produk tetap membutuhkan workflow approval yang eksplisit sebelum konten masuk ke tahap scheduling atau publishing agar kualitas hasil tetap terjaga.[cite:121][cite:167]

Cakupan MVP mencakup pembuatan brief, generasi konten multi-format, penyimpanan style guide dan CTA pattern, approval flow, content calendar, scheduler bawaan, autopost YouTube hingga scheduled publish, analytics publish dasar, dan arsitektur yang siap diperluas ke TikTok serta X.[cite:118][cite:121][cite:144] Fitur generate image dan video tidak masuk MVP penuh, tetapi harus disiapkan sebagai ekstensi “coming soon” dalam struktur data dan UX produk.[cite:120][cite:136]

## Supported Content Types

Produk harus mendukung tipe konten berikut pada fase awal:

| Content Type | Status MVP | Notes |
|---|---|---|
| YouTube Shorts | Ya | Script, title, thumbnail brief/prompt, scheduling, autopost.[cite:144][cite:148] |
| YouTube Long-form | Ya | Script outline/full script, title, description, scheduling, autopost.[cite:144] |
| TikTok Short Video | Ya, generation + scheduler design | Publish integration dapat disiapkan bertahap sesuai API/platform constraints.[cite:127] |
| Blog Article | Ya | Brief, outline, draft article, CTA, publishing-ready export.[cite:121][cite:141] |
| X Post Caption | Ya | Hook, thread/caption options, CTA, scheduling design.[cite:121][cite:127] |

Bahasa utama produk dan output default adalah Bahasa Indonesia, dengan Bahasa Inggris sebagai opsi sekunder untuk prompt, brief, dan hasil generasi konten.[cite:121][cite:124]

## Key Use Cases

Use case utama meliputi pembuatan campaign konten, penyusunan brief, generasi draft multi-format, review manual, approval, penjadwalan di content calendar, dan autopost sesuai channel.[cite:118][cite:121][cite:140] Produk juga harus mendukung penyimpanan style guide dan CTA pattern agar tiap generasi mengikuti identitas konten yang telah ditentukan.[cite:121][cite:124]

Use case utama:
- Menyusun ide dan brief untuk YouTube Shorts atau long-form dalam Bahasa Indonesia.[cite:121]
- Menghasilkan beberapa varian judul, hook, CTA, dan struktur script dari satu brief.[cite:118][cite:136]
- Menyimpan style guide seperti tone, vocabulary rules, banned phrases, dan CTA pattern.[cite:121][cite:124]
- Melakukan approval manual sebelum konten dapat dijadwalkan.[cite:167]
- Menjadwalkan publish ke YouTube sampai level scheduled publish menggunakan OAuth 2.0 dan YouTube Data API flow.[cite:144][cite:145][cite:149]
- Menyusun konten untuk TikTok, blog, dan X dari satu ide sumber yang sama.[cite:121][cite:127]
- Memantau analytics operasional seperti jumlah konten, status publish, kegagalan upload, dan penggunaan provider/model.[cite:136][cite:138]

## Functional Requirements

### 1. Authentication

Sistem harus menyediakan autentikasi sederhana berbasis username dan password untuk penggunaan internal tunggal tanpa social login.[cite:20] Karena produk digunakan di production pribadi pada VPS self-hosted, implementasi harus tetap aman melalui password hashing, session management, rate limiting dasar, dan akses HTTPS di reverse proxy.[cite:20][cite:129]

Kebutuhan:
- Login/logout dengan username dan password.
- Password disimpan dengan hashing yang kuat.
- Session timeout yang wajar.
- Audit login sederhana.

### 2. Workspace Model

Meskipun single-user, aplikasi tetap membutuhkan struktur organisasi internal berupa workspace pribadi, brand profile, campaign, dan content item agar workflow tidak bercampur.[cite:118][cite:121] Struktur ini juga mempermudah ekspansi jangka panjang bila nanti beberapa brand atau niche konten ingin dikelola dalam tool yang sama.[cite:121]

Entitas minimum:
- Brand / Channel
- Campaign
- Content Item
- Content Version
- Publish Job
- Style Guide
- CTA Pattern

### 3. Brief Builder

Brief builder harus menjadi titik awal semua workflow agar hasil generasi lebih terstruktur dan konsisten.[cite:121][cite:141] Form brief minimal harus mencakup platform target, format konten, topik, audience, objective, key message, tone, CTA, referensi, dan bahasa output.[cite:121]

Kebutuhan:
- Template brief per platform.
- Input manual dan clone dari brief lama.
- Brief bilingual ID/EN.
- Penyimpanan referensi dan notes.

### 4. Content Generation

Sistem harus mendukung generasi multi-format dengan model/provider yang dapat dipilih per run atau melalui default preset.[cite:129][cite:140] Hasil generasi perlu mendukung beberapa variasi output seperti beberapa judul, hook alternatif, CTA, thumbnail brief/prompt, dan script isi konten.[cite:118][cite:136]

Output minimum per format:
- YouTube Shorts: title, hook, short script, thumbnail brief/prompt, description draft.[cite:144]
- YouTube Long-form: title, outline, full script draft, description draft, thumbnail brief/prompt.[cite:144]
- TikTok: hook, short script, caption, visual cue notes.[cite:127]
- Blog: title, outline, article draft, CTA placement.[cite:121]
- X: short post, long post/thread draft, CTA variants.[cite:127]

### 5. Multi-Provider AI Layer

Produk harus memiliki abstraction layer untuk multi-provider agar bisa berpindah model sesuai biaya, kualitas, atau kebutuhan task tertentu.[cite:129][cite:132] Layer ini harus menyimpan metadata provider, model, prompt template, token usage, latency, dan status run untuk analisis operasional.[cite:130][cite:133]

Kebutuhan:
- Konfigurasi provider dan model.
- Default provider per task type.
- Logging usage per generation run.
- Failover/manual retry.

### 6. Style Guide and CTA Memory

Sistem harus menyimpan style guide dan CTA pattern yang dapat dipakai ulang di setiap generasi agar output lebih konsisten.[cite:121][cite:124] Data ini harus dapat diedit, diaktifkan/nonaktifkan, serta dipilih per brand, campaign, atau content item.[cite:121]

Isi minimum style guide:
- Tone of voice.
- Writing rules.
- Preferred phrases.
- Banned phrases.
- CTA library.
- Brand examples / reference outputs.

### 7. Approval Workflow

Semua konten wajib melewati tahap approval manual sebelum masuk ke scheduler atau autopost queue.[cite:167] Status minimum yang harus didukung adalah draft, in review, approved, scheduled, published, failed, dan archived.[cite:121][cite:167]

Rules:
- Konten tanpa approval tidak bisa dijadwalkan.
- Revisi membuat versi baru atau menyimpan revision history.
- Approval action harus tercatat di audit trail.

### 8. Content Calendar and Scheduler

Produk harus memiliki content calendar bawaan agar semua rencana publish dapat dilihat per hari, minggu, dan bulan.[cite:127][cite:141] Scheduler harus mendukung publish now dan scheduled publish, termasuk pengelolaan timezone yang konsisten untuk VPS dan target platform.[cite:144][cite:148]

Kebutuhan:
- Calendar view bulanan dan mingguan.
- Drag-and-drop opsional untuk ubah jadwal.
- Queue status per item.
- Publish now / schedule later.
- Retry atau reschedule saat gagal.

### 9. Platform Integrations

#### YouTube

Integrasi YouTube wajib mendukung OAuth 2.0 server-side flow, token refresh, upload video, metadata submission, dan scheduled publish workflow.[cite:144][cite:145][cite:149] Scope minimal yang dipakai harus mengikuti kebutuhan upload video, dan token harus disimpan aman karena dipakai ulang oleh background job.[cite:145][cite:148]

Kebutuhan YouTube:
- Connect/disconnect channel.
- Simpan refresh token secara aman.
- Upload video dengan title, description, tags, privacy status, publish schedule.[cite:144]
- Track upload status, response ID, dan error logs.[cite:144][cite:148]

#### TikTok

Pada MVP, TikTok harus didukung minimal pada level content planning, script generation, caption generation, dan scheduler-ready architecture.[cite:127] Jika API autopost resmi tersedia dan feasible untuk akun pengguna, integrasi publish dapat diaktifkan bertahap; jika belum, sistem harus tetap menghasilkan paket publish-ready yang bisa dipakai manual.[cite:127]

#### X

Pada MVP, X harus didukung untuk generation, queueing, scheduling design, dan publish-ready output.[cite:127] Implementasi autopost ke X bergantung pada akses API, batasan biaya, dan kebijakan platform, sehingga PRD harus menganggap channel ini sebagai staged rollout setelah validasi teknis selesai.[cite:127]

### 10. Analytics MVP

Analytics pada MVP harus fokus pada operasional produk, bukan performa marketing yang sangat mendalam.[cite:136][cite:138] Dashboard minimal harus menampilkan jumlah konten per status, jumlah publish berhasil/gagal, konten terjadwal, penggunaan model/provider, serta ringkasan aktivitas per platform.[cite:136][cite:138]

Metrix minimum:
- Draft created count
- Approved count
- Scheduled count
- Published count
- Failed publish count
- Provider/model usage
- Average generation latency
- Recent publish activity

### 11. Assets and Coming Soon Features

Pada fase saat ini, produk hanya perlu menghasilkan thumbnail brief/prompt, script isi konten, dan judul.[cite:120][cite:136] Namun, struktur data, UI copy, dan roadmap harus menyiapkan jalur ekspansi untuk generate image dan video sebagai fitur coming soon tanpa perlu refactor besar.[cite:120][cite:123]

## Non-Functional Requirements

Karena produk ini dipakai pribadi tetapi benar-benar production, stabilitas, backup, logging, dan keamanan operasional menjadi penting.[cite:20][cite:129] Sistem harus bisa berjalan baik di VPS self-hosted dengan komponen yang dapat dipantau dan dipulihkan bila terjadi error.[cite:20]

Kebutuhan non-fungsional:
- HTTPS wajib di depan aplikasi melalui Nginx reverse proxy.[cite:20]
- Backup rutin database dan asset metadata.
- Centralized logs untuk app, worker, dan publish jobs.
- Retry mechanism untuk background job gagal.[cite:144][cite:148]
- Token dan secret disimpan aman, idealnya terenkripsi di level aplikasi atau secret store.[cite:148][cite:149]
- Sistem harus tetap usable meski satu provider AI gagal, melalui fallback manual atau failover provider.[cite:129][cite:140]
- Bahasa UI utama Indonesia dengan kemampuan secondary English.

## Recommended Tech Stack

| Layer | Recommended Stack | Reason |
|---|---|---|
| Frontend | Next.js + TypeScript + Tailwind CSS | Cocok untuk dashboard, calendar, forms, dan internal tooling modern.[cite:135][cite:139] |
| Backend | FastAPI | Ringan, cepat, cocok untuk API, worker orchestration, dan OAuth callbacks.[cite:19][cite:129] |
| Database | PostgreSQL | Stabil untuk relational workflow data dan analytics operasional.[cite:19][cite:133] |
| Queue / Jobs | Redis + Celery | Cocok untuk scheduling, generation jobs, publish jobs, dan retry handling.[cite:129][cite:139] |
| Storage | S3-compatible / Cloudflare R2 / local object storage | Untuk simpan asset dan file publish-ready.[cite:129] |
| Reverse Proxy | Nginx | Cocok untuk HTTPS, routing, dan self-hosted VPS deployment.[cite:20] |
| Auth | Username/password custom session auth | Sesuai scope internal tool single-user.[cite:20] |
| AI Provider Layer | Multi-provider adapter (OpenAI, Gemini, Anthropic, local models) | Memberi fleksibilitas kualitas dan biaya.[cite:129][cite:132] |
| Vector/Memory | pgvector atau Qdrant (optional in MVP) | Untuk reference retrieval, style memory, dan semantic recall jangka lanjut.[cite:131][cite:134] |

## Data Model Summary

Tabel inti yang dibutuhkan:
- `users`
- `brands`
- `campaigns`
- `style_guides`
- `cta_patterns`
- `content_items`
- `content_versions`
- `generation_runs`
- `platform_accounts`
- `oauth_tokens`
- `publish_jobs`
- `publish_logs`
- `analytics_daily_snapshots`

Relasi inti:
- Satu user memiliki banyak brand dan campaign.
- Setiap campaign memiliki banyak content item.
- Setiap content item memiliki banyak version dan publish job.
- Style guide dan CTA pattern dapat dihubungkan ke brand atau campaign.
- OAuth token dihubungkan ke platform account yang aktif.[cite:145][cite:149]

## API and Module Outline

Modul backend minimum:
- Auth module
- Brand/Campaign module
- Brief Builder module
- Generation module
- Style Guide module
- Approval module
- Calendar/Scheduler module
- Platform Integration module
- Analytics module
- Audit Log module

Endpoint minimum contoh:
- `POST /auth/login`
- `POST /auth/logout`
- `GET /brands`
- `POST /campaigns`
- `POST /content/generate`
- `POST /content/{id}/approve`
- `POST /schedule`
- `GET /calendar`
- `GET /integrations/youtube/connect`
- `GET /integrations/youtube/callback`
- `POST /publish/{id}/run`
- `GET /analytics/overview`

## User Flow

Alur utama produk:
1. User login ke dashboard internal.[cite:20]
2. User membuat atau memilih brand dan campaign.
3. User membuat brief baru untuk platform tertentu.[cite:121]
4. Sistem menghasilkan beberapa draft konten berdasarkan provider/model terpilih.[cite:129][cite:140]
5. User memilih hasil terbaik, revisi bila perlu, lalu menandai konten sebagai approved.[cite:167]
6. User menambahkan jadwal di content calendar.[cite:127][cite:141]
7. Worker memproses scheduled job pada waktunya.[cite:129][cite:139]
8. Untuk YouTube, sistem menggunakan refresh token OAuth 2.0 untuk upload dan publish sesuai jadwal.[cite:144][cite:145][cite:149]
9. Sistem mencatat hasil publish dan memperbarui analytics dashboard.[cite:136][cite:138]

## MVP Scope

Fitur MVP yang harus dibangun terlebih dahulu:
- Login username/password.
- Brand, campaign, dan content item management.
- Brief builder.
- Multi-format content generation.
- Style guide dan CTA pattern memory.
- Approval workflow wajib.
- Content calendar dan scheduler.
- YouTube OAuth 2.0 connect + scheduled publish autopost.[cite:144][cite:145]
- TikTok dan X generation support + scheduler-ready structure.[cite:127]
- Analytics operasional dasar.[cite:136][cite:138]

Di luar MVP tetapi sudah disiapkan struktur dasarnya:
- Image generation.
- Video generation.
- Deep analytics per performance channel.
- Advanced retrieval memory.
- Fully automated TikTok/X autopost setelah validasi kebijakan dan API platform.[cite:120][cite:123][cite:127]

## Success Criteria

Produk dianggap berhasil pada fase awal bila mampu menjalankan workflow harian tanpa friksi tinggi, menghasilkan draft yang reusable, menjaga approval discipline, dan mempublikasikan konten YouTube terjadwal secara reliabel.[cite:144][cite:148] Keberhasilan MVP diukur dari kestabilan operasi dan penghematan waktu kerja, bukan skala jumlah user.[cite:20][cite:136]

Kriteria keberhasilan awal:
- Konten bisa dibuat dari brief ke approved state dalam satu alur terpadu.
- Scheduled publishing YouTube berjalan stabil untuk kebutuhan pribadi.[cite:144][cite:148]
- Kalender konten memudahkan perencanaan mingguan/bulanan.[cite:127][cite:141]
- Prompt/style memory membantu menjaga konsistensi output.[cite:121][cite:124]
- Analytics cukup untuk mengetahui apa yang berjalan, gagal, dan perlu diperbaiki.[cite:136][cite:138]

## Open Questions

Beberapa poin masih perlu validasi teknis lebih lanjut sebelum build final:
- Sejauh mana API TikTok mendukung autopost untuk akun dan use case yang ditargetkan.[cite:127]
- Sejauh mana API X layak dipakai untuk autopost dalam konteks biaya dan policy.[cite:127]
- Apakah metadata performa channel eksternal juga akan ditarik masuk, atau analytics MVP hanya fokus pada publish operations.[cite:136][cite:138]
- Apakah vector memory perlu masuk MVP, atau cukup penyimpanan style guide terstruktur terlebih dahulu.[cite:131][cite:134]

## Recommended Next Step

Langkah berikut yang paling disarankan adalah membuat system architecture, database schema rinci, dan implementation roadmap berbasis fase build agar MVP bisa dibangun bertahap tanpa scope creep.[cite:159][cite:162][cite:167]
