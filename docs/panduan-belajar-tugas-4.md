# Panduan membaca implementasi Tugas 4

Panduan ini mengikuti kode akhir proyek. Untuk instalasi dan langkah membuat Editor, gunakan README terlebih dahulu.

## 1. Mulai dari masalah yang diperbaiki

Pada Tugas 3, form Experience sudah dapat menambah, mengedit, dan menghapus data. Pada Tugas 4, kemampuan tersebut perlu dibatasi berdasarkan identitas pengguna. Menyembunyikan tombol belum cukup karena seseorang masih dapat mengirim permintaan langsung ke URL. Karena itu, pembatasan diterapkan pada view yang menerima permintaan.

Buka `main/urls.py` untuk melihat hubungan URL dan view:

| URL Experience | View | Tujuan |
|---|---|---|
| `/experience/` | `show_experience` | Daftar publik |
| `/experience/<uuid>/` | `experience_detail` | Detail publik |
| `/experience/add/` | `create_experience` | Form tambah milik pemilik |
| `/experience/<uuid>/edit/` | `update_experience` | Form edit pemilik/Editor |
| `/experience/<uuid>/delete/` | `delete_experience` | Hapus lewat POST oleh pemilik |
| `/experience/<uuid>/star/` | `toggle_experience_star` | Star/unstar pengguna yang login |
| `/api/experiences/` | `get_experiences_json` | Data JSON publik |

UUID adalah ID objek Experience. URL tidak menentukan hak akses; view tetap memeriksa pengguna yang membuat permintaan.

## 2. Pahami pemeriksaan peran

Buka `main/permissions.py`. Fungsi `is_editor(user)` memeriksa apakah pengguna sudah login dan menjadi anggota grup bernama `Editor`.

Decorator `portfolio_permission_required()` menerima argumen `allow_editor`:

```python
@portfolio_permission_required()
def create_experience(request):
    ...

@portfolio_permission_required(allow_editor=True)
def update_experience(request, experience_id):
    ...
```

Tanpa `allow_editor=True`, hanya superuser yang lolos. Dengan opsi tersebut, superuser dan anggota Editor diizinkan. `login_required` menangani pengunjung, sedangkan `PermissionDenied` menghasilkan HTTP 403 bagi akun yang sudah login tetapi tidak berhak.

Untuk delete, susunannya adalah:

```python
@portfolio_permission_required()
@require_POST
def delete_experience(request, experience_id):
    ...
```

Pemeriksaan login/izin terjadi sebelum pemeriksaan metode di dalam decorator POST. Pengunjung yang membuka URL delete diarahkan ke login; pengguna biasa/Editor menerima 403; superuser yang mengaksesnya lewat GET mendapat 405. POST yang lolos izin dan CSRF dapat menghapus objek.

CSRF diproses oleh middleware sebelum view. Karena itu, POST tanpa token valid dapat menghasilkan 403 bahkan sebelum decorator memeriksa apakah pengguna sudah login.

## 3. Hubungkan peran dengan tampilan

View daftar dan detail mengirim `is_editor` ke template. Di `templates/experience.html` dan `templates/experience_detail.html`, Edit dibungkus kondisi:

```django
{% if user.is_superuser or is_editor %}
    ... tombol Edit ...
{% endif %}
```

Add dan Delete hanya dibungkus `user.is_superuser`. Hasilnya, pengguna melihat tindakan yang sesuai dengan izinnya. Jika kondisi template dihapus, server tetap menolak tindakan terlarang karena decorator tidak bergantung pada tampilan.

## 4. Pahami relasi star pada model

Buka `main/models.py`:

```python
starred_by = models.ManyToManyField(
    settings.AUTH_USER_MODEL,
    related_name="starred_experiences",
    blank=True,
)
```

Satu Experience dapat diberi star banyak pengguna, dan satu pengguna dapat memberi star pada banyak Experience. `related_name` menyediakan akses kebalikan dari pengguna ke Experience yang dibintanginya. `blank=True` berarti Experience boleh belum mempunyai pemberi star.

Perubahan model menghasilkan migrasi `0006_experience_starred_by.py`. Migrasi membuat tabel penghubung beserta batasan unik pasangan ID Experience dan ID pengguna. Menjalankan `makemigrations` membuat instruksi perubahan skema; menjalankan `migrate` menerapkannya ke database.

Field `starred_by` tidak masuk `ExperienceForm`, sehingga form edit portofolio tidak dapat menentukan pemberi star.

## 5. Ikuti satu klik tombol star

Alurnya:

1. Browser menampilkan form dari `templates/components/experience_star.html`.
2. Form memakai `method="post"`, URL star objek terkait, dan `{% csrf_token %}`.
3. Django memvalidasi CSRF dan autentikasi.
4. View mencari Experience dengan `get_object_or_404`.
5. View memeriksa apakah `request.user` sudah ada dalam `experience.starred_by`.
6. Jika sudah ada, relasi pengguna itu dihapus. Jika belum, relasi ditambahkan.
7. View mengirim pesan sukses dan redirect ke daftar atau detail asal.
8. Browser mengambil halaman kembali sehingga jumlah dan status tombol diperbarui.

Tidak ada ID pengguna yang perlu dikirim oleh form. Menggunakan `request.user` memastikan pengguna hanya mengatur starnya sendiri. Redirect setelah POST juga mencegah refresh halaman hasil secara langsung mengirim ulang form sebelumnya.

Pada template, `aria-pressed` menjelaskan status tombol kepada teknologi bantu. Tulisan Star/Unstar menjelaskan aksi berikutnya, sedangkan angka menunjukkan total seluruh pengguna.

## 6. Pahami pemisahan JSON publik dan status pengguna

Buka `get_experiences_json` dan `get_projects_json`. Keduanya menggunakan `fields=(...)` untuk memilih hanya data portofolio yang boleh diserialisasi. Field `starred_by` tidak disertakan. Format hasil tetap berupa daftar objek dengan `model`, `pk`, dan `fields` agar sesuai pola Tugas 3.

`deserialize_with_star_status` mengubah JSON kembali menjadi objek untuk tampilan daftar. Setelah itu, `with_star_status` menambahkan dua nilai:

- `star_count`: jumlah pengguna yang memberi star, dihitung dengan `Count`.
- `is_starred`: apakah pengguna aktif sudah memberi star, diperiksa dengan `Exists`.

Untuk pengunjung, `is_starred` bernilai false. Proses ini tidak memerlukan penampilan username atau email pemberi star. Daftar juga tidak melakukan kueri seluruh pengguna pada setiap kartu hanya untuk menampilkan jumlah star.

## 7. Ikuti login dan logout

`login_user` memakai `AuthenticationForm`. Setelah form valid, `login(request, user)` membentuk session Django. Cookie `last_login` menyimpan waktu untuk ditampilkan di beranda, dengan penanda zona waktu.

Parameter `next` menyimpan halaman tujuan setelah login. Nilainya dipertahankan sebagai input tersembunyi pada form dan diperiksa dengan `url_has_allowed_host_and_scheme`. Tujuan luar host aplikasi ditolak dan diganti beranda. Mekanisme ini menghindari redirect ke situs lain yang disisipkan lewat tautan login.

Logout menggunakan form POST pada navbar, bukan tautan GET. View `logout_user` mengakhiri session dan menghapus cookie `last_login`. Mengedit cookie `last_login` tidak memberi hak Editor ataupun superuser karena cookie tersebut hanya untuk informasi tampilan.

## 8. Baca tes berdasarkan skenarionya

`main/tests.py` berisi kelompok tes berikut:

| Kelas tes | Hal yang diperiksa |
|---|---|
| `MainTest` | Halaman publik dan tampilan data |
| `ProjectFlowTest` | Form dan operasi Projects oleh pemilik |
| `ExperienceFlowTest` | Form dan operasi Experience oleh pemilik |
| `ExperienceAccessTest` | Penolakan/pemberian akses sesuai peran |
| `ExperienceStarTest` | Star, jumlah, CSRF, detail, dan JSON Experience |
| `AuthAndProjectSecurityTest` | Login/logout, registrasi, serta keamanan Projects |
| `AssignmentFourRegressionTest` | Alur Admin, CSRF semua aksi, role/detail, dan perlindungan data |

Contoh cara menjalankan bagian tertentu:

```bash
python manage.py test main.tests.ExperienceAccessTest
python manage.py test main.tests.ExperienceStarTest
python manage.py test main.tests.AssignmentFourRegressionTest
```

Untuk pemeriksaan lengkap, jalankan `python manage.py test`. Tes membuat database sementara; akun di dalam tes bukan akun yang bisa dipakai login ke database portofolio utama.

## 9. Bedakan kode, database, hosting, dan pengumpulan

- **Commit** menyimpan perubahan kode di repository lokal.
- **Push** mengirim commit ke GitHub.
- **Migrasi dan pengaturan grup** bekerja pada database masing-masing lingkungan.
- **Deployment** menerapkan kode pada hosting dan bukan akibat otomatis dari setiap push GitHub, kecuali pipeline memang telah disiapkan.
- **Pengumpulan SCELE** dilakukan dengan tautan commit final melalui akun mahasiswa.

Karena akun dan grup tidak disimpan sebagai kode, jangan menganggap akun Editor lokal otomatis muncul di hosting. Gunakan Django Admin di lingkungan yang ingin diuji untuk menetapkan perannya.
