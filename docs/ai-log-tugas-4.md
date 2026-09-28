# Ringkasan bantuan AI — Tugas 4

Tanggal: 28 September 2026.
Alat: OpenAI Codex pada sesi ChatGPT/Codex, terminal, dan otomasi browser.
Dokumen ini adalah ringkasan interaksi dan hasil kerja, bukan transkrip percakapan lengkap.

## Permintaan dan keputusan

1. Pengguna memberikan tautan instruksi Tugas 4 dan meminta pengerjaan langkah demi langkah, sekitar lima commit sebelum push, dengan jarak waktu 5–25 menit dan target selesai sebelum 23.15 WIB. Pengguna meminta rencana commit untuk disetujui terlebih dahulu.
2. Codex membaca instruksi dan memeriksa proyek tanpa mengubah kode. Ditemukan bahwa Experience belum dilindungi otorisasi dan belum memiliki star. Pemeriksaan awal menemukan 24 tes dengan empat kegagalan akibat tes Projects yang belum menyesuaikan kebutuhan login.
3. Codex mengusulkan lima tahap: izin peran, star Experience, keamanan JSON/alur autentikasi, pengujian, dan dokumentasi.
4. Pengguna meminta contoh AI disclosure, kemudian memberikan versi yang lebih singkat dan mengizinkan pengerjaan dimulai. Versi akhir dibuat ringkas dan menyebut bantuan pemahaman serta implementasi kode agar sesuai penggunaan AI dalam sesi ini.
5. Codex menulis perubahan kode dan tes, menjalankan migrasi lokal, memeriksa hasil melalui browser, serta menyiapkan commit. Pengguna menerima pembaruan progres selama pengerjaan.

## Bagian yang dibantu AI

| Bagian | Bentuk bantuan |
|---|---|
| Otorisasi | Menulis helper pemeriksaan superuser/Editor dan menerapkannya pada view serta template |
| Star Experience | Menambahkan model ManyToMany, migrasi, endpoint POST, tombol, serta hitungan/status star |
| Tampilan | Menambahkan detail Experience publik dan kontrol sesuai hak akses |
| JSON | Membatasi field yang diserialisasi agar identitas akun pemberi star tidak ikut dipublikasikan |
| Autentikasi | Memvalidasi tujuan login dan menerapkan logout melalui POST dengan CSRF |
| Projects | Menambahkan edit bagi pemilik/Editor dan menyamakan pemeriksaan keamanan |
| Verifikasi | Menulis tes otomatis dan mengoperasikan browser pada database sementara |
| Dokumentasi/Git | Menyusun README, catatan pengujian, log ini, serta commit bertahap |

## Keterbatasan AI dan koreksi selama pengerjaan

- Pemeriksaan pertama memakai environment lokal Django 4.2, sedangkan `requirements.txt` menyebut 5.2. Lolos pada environment lama belum cukup untuk menyatakan kompatibilitas dependency proyek. Codex kemudian membuat environment terpisah Python 3.12/Django 5.2 dan menguji kedua versi.
- Salah satu penggantian teks saat menambah route edit Projects sempat memasukkan fungsi ekstra ke deklarasi route delete. Pemeriksaan Django mendeteksi `TypeError` sebelum commit tahap tersebut. Codex memperbaiki deklarasi URL, lalu menjalankan kembali tes hingga lolos. Ini menunjukkan bahwa perubahan otomatis tetap membutuhkan pemeriksaan nyata.
- Tes lama menganggap pengunjung boleh menjalankan aksi pemilik. Tes tersebut diperbaiki agar menggunakan superuser; tes penolakan akses ditambahkan secara terpisah agar pembatasan keamanan tidak dilonggarkan hanya demi meloloskan tes.
- Perhitungan status star dipisahkan dari serializer publik. Hal ini mempertahankan alur JSON/deserialisasi dari Tugas 3 tanpa mengekspos relasi akun pada endpoint publik.
- AI tidak dapat mengisi pertanyaan reflektif yang belum diterbitkan. README menandai placeholder dan hanya menjelaskan implementasi yang benar-benar tersedia.
- Pemeriksaan browser dan tes pada sesi ini dijalankan oleh Codex. Dokumen ini tidak mengklaim mahasiswa menulis seluruh kode atau menguji seluruh alur sendiri, dan tidak menyatakan bahwa pemeriksaan lokal menjamin semua kondisi produksi.

## Bukti yang dapat ditinjau

- Implementasi: `main/permissions.py`, `main/models.py`, `main/views.py`, `main/urls.py`, dan template terkait.
- Migrasi: `main/migrations/0006_experience_starred_by.py`.
- Tes otomatis: `main/tests.py`.
- Hasil pemeriksaan: [pengujian-tugas-4.md](pengujian-tugas-4.md).
- Riwayat perubahan: lima commit bertahap dalam Git, dengan timestamp waktu pengerjaan sebenarnya.
