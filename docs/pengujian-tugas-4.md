# Catatan pengujian Tugas 4

Pengujian dilakukan pada 28 September 2026. Perintah dijalankan dari direktori yang berisi `manage.py`.

## Pemeriksaan otomatis

| Pemeriksaan | Hasil |
|---|---|
| `python manage.py check` | Lolos; tidak ada masalah pada system check |
| `python manage.py makemigrations --check --dry-run` | Lolos; tidak ada perubahan model yang belum dimigrasikan |
| Migrasi database lokal sampai `0006_experience_starred_by` | Berhasil |
| Migrasi dari database kosong untuk pengujian browser | Berhasil |
| 55 tes pada Python 3.12.14 / Django 5.2.17 | Seluruhnya lolos |
| 55 tes pada environment lama Python 3.9 / Django 4.2.30 | Seluruhnya lolos |
| `git diff --check` | Tidak ada kesalahan whitespace |
| `runserver` dengan Django 5.2 | Berjalan dan melayani halaman tanpa error 500 |

Environment Django 5.2 dibuat terpisah untuk menguji dependency yang tertulis di `requirements.txt`; environment lama proyek tidak diganti. Tes menggunakan database sementara yang dibuat dan dibuang oleh Django TestCase. WhiteNoise mengeluarkan pemberitahuan bahwa direktori `staticfiles/` belum dibuat; ini bukan kegagalan tes. Pada development server, berkas CSS tetap tersedia melalui staticfiles finders. Deployment yang mengumpulkan berkas statis perlu menjalankan `python manage.py collectstatic --noinput`.

## Cakupan tes

- Daftar Experience dan Projects tetap publik, termasuk keadaan kosong, status selesai, serta pencarian judul Projects.
- Pengunjung diarahkan ke login saat membuka aksi yang dilindungi.
- Pengguna biasa menerima 403 untuk create, update, dan delete melalui URL langsung.
- Editor dapat mengedit; create dan delete tetap ditolak.
- Superuser dapat membuat, memperbarui, serta menghapus dengan metode yang benar.
- Tombol pada daftar dan detail mengikuti hak akses.
- Flag staff saja tidak memberi hak pengelolaan portofolio; pencabutan grup Editor mencabut hak edit.
- Pemilik dapat membuat grup dan menetapkan Editor melalui view Django Admin; Editor tetap bukan staff/superuser.
- Registrasi tidak dapat menerima peningkatan hak akses lewat field POST tambahan.
- Semua peran yang login dapat memberi star. Unstar hanya mengubah relasi pengguna aktif.
- Duplikasi relasi pengguna–Experience tidak menghasilkan dua star.
- GET tidak mengubah star, menghapus data, atau mengakhiri session.
- POST tanpa token CSRF ditolak pada seluruh aksi perubahan, termasuk untuk superuser.
- Token CSRF yang valid memungkinkan operasi star yang sah.
- Form edit tidak dapat menimpa daftar pemberi star melalui field tambahan.
- JSON mempertahankan format publik tanpa field `starred_by` atau username pemberi star.
- Form tidak valid tidak mengubah data yang tersimpan.
- Konten HTML yang dimasukkan dalam judul/deskripsi di-escape di template.
- Login mempertahankan `next` lokal, menolak tujuan eksternal, dan mempertahankan tujuan saat password salah.
- Logout menghapus session dan cookie `last_login`.
- Detail atau star untuk Experience yang tidak ada menghasilkan 404.

## Pemeriksaan melalui browser

Pengujian interaktif menggunakan database sementara terpisah dengan tiga akun QA: pemilik, Editor, dan pengguna biasa. Akun dan password QA tidak disertakan dalam repository. Data portofolio asli tidak digunakan untuk percobaan edit atau pemberian star.

1. Membuka daftar Experience tanpa login: data dan tautan JSON tersedia; tombol tambah, edit, dan hapus tersembunyi.
2. Membuka detail Experience tanpa login: judul, deskripsi, status, jumlah star, dan tautan login tersedia.
3. Login ke Django Admin sebagai pemilik QA, membuat grup `Editor`, kemudian memasukkan akun Editor melalui form Users. Staff/superuser pada akun Editor tetap tidak dicentang.
4. Login melalui `/login/?next=/experience/` sebagai Editor: browser kembali ke Experience; tombol Edit tersedia tanpa Add/Delete.
5. Memberi star pada Experience sebagai Editor: pesan sukses dan status Unstar tampil.
6. Mengedit Experience dan Projects sebagai Editor: perubahan tersimpan dan pesan sukses tampil.
7. Logout: kembali ke beranda dengan navigasi Login/Register dan informasi bahwa cookie login tidak ditemukan.
8. Login sebagai pengguna biasa: daftar Experience menampilkan star tanpa tombol pengelolaan data.
9. Pada detail Experience, memberi star mengubah jumlah 1 menjadi 2. Unstar mengembalikannya menjadi 1, sehingga star milik Editor tetap ada. Browser tetap berada pada halaman detail.
10. Memeriksa detail pada viewport 390 × 844: lebar halaman 390 px, sama dengan viewport; tidak ada overflow horizontal. Viewport kemudian dikembalikan ke ukuran semula.

Pemeriksaan browser dilakukan oleh Codex menggunakan alat otomasi browser, bukan klaim pemeriksaan manual oleh mahasiswa. Keberhasilan pada environment lokal tidak menyatakan bahwa deployment PWS atau pengumpulan SCELE sudah dilakukan.

## Menjalankan ulang

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py runserver
```

Untuk uji role melalui browser pada instalasi sendiri, ikuti langkah pengaturan Editor di README. Peran dan akun harus dibuat pada database lingkungan tersebut; keduanya bukan bagian dari kode Git.

## Pemeriksaan sebelum push

- Endpoint lokal `/`, `/experience/`, `/projects/`, `/api/experiences/`, `/api/projects/`, `/login/`, dan `/register/` semuanya mengembalikan HTTP 200.
- Kedua endpoint API mengembalikan `application/json` dan tidak memiliki field `starred_by`.
- GitHub API dapat membaca repository tanpa autentikasi dan melaporkan `private: false`.
- `git push --dry-run origin main` berhasil; pemeriksaan ini tidak mengirim commit ke remote.
