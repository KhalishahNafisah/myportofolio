# Portofolio Khalishah Nafisah

Website portofolio untuk mata kuliah Pemrograman Berbasis Platform, menggunakan Django, HTML, dan CSS. Bagian dinamisnya mencakup Projects dan Experience, form pengelolaan data, API JSON publik, autentikasi, dan star per pengguna.

## Menjalankan proyek dari awal

Gunakan Python 3.12 untuk mengikuti environment pengujian Django 5.2. Environment lama `env/` pada komputer pengembangan masih menggunakan Python 3.9/Django 4.2; buat environment baru untuk mengikuti `requirements.txt`.

```bash
git clone https://github.com/KhalishahNafisah/myportofolio.git
cd myportofolio
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py check
python manage.py test
python manage.py runserver
```

Pada Windows, aktivasi environment menggunakan `.venv\Scripts\activate`. Jika repository sudah tersedia, mulai dari direktori yang berisi `manage.py`; tidak perlu clone ulang. Konfigurasi lokal menggunakan SQLite dengan `PRODUCTION=False` (nilai default). Jangan menyalin `.env.prod` atau kredensial produksi ke repository.

Buka `http://127.0.0.1:8000/`. Jika port tersebut sedang dipakai, jalankan `python manage.py runserver 8005` dan buka port yang sama di browser. Clone baru memiliki database kosong; masuk dengan akun superuser dan tambahkan Projects/Experience lewat form website atau Django Admin.

| Halaman | URL |
|---|---|
| Beranda dan informasi sesi | `/` |
| Daftar Experience | `/experience/` |
| Detail Experience | `/experience/<uuid>/` |
| Daftar dan pencarian Projects | `/projects/` |
| JSON Experience | `/api/experiences/` |
| JSON Projects | `/api/projects/` |
| Registrasi dan login | `/register/`, `/login/` |
| Pengaturan pengguna dan grup | `/admin/` |

Database, password, dan akun lokal tidak ikut di-push. Pada instalasi atau deployment baru, jalankan migrasi dan atur akun/peran pada database lingkungan tersebut. Push GitHub menyimpan kode; penerapan ke hosting adalah langkah terpisah.

## Identitas dan progres mingguan

Nama : Khalishah Nafisah

NPM : 2506605840

Kelas : PBP E

Dosen : Pak Daya

### Tugas 1
1. Iya, saya menggunakan elemen semantik HTML5 seperti <section> untuk membagi website menjadi beberapa bagian, seperti About Me, Projects, dan Contact. Penggunaan elemen semantik membantu saya membuat struktur HTML yang lebih terorganisir dan mudah dipahami. Selain itu, struktur tersebut juga memudahkan saya ketika mengatur CSS karena setiap bagian website memiliki struktur yang jelas.
2. Tantangan utama yang saya temukan adalah menyesuaikan ukuran dan posisi beberapa elemen agar tetap terlihat rapi pada layar yang lebih kecil. Misalnya, layout yang menggunakan beberapa kolom pada desktop perlu diubah menjadi satu kolom pada mobile. Saya mengevaluasinya dengan melihat prioritas informasi dan ukuran layar. Elemen yang paling penting saya tempatkan lebih awal dan ukurannya disesuaikan, sedangkan elemen yang kurang penting dapat dibuat lebih kecil atau dipindahkan ke bagian bawah.
3. Karena website masih berupa static web, informasi di dalamnya masih harus diubah secara manual melalui kode HTML dan CSS. Hal ini cukup membatasi ketika ingin memperbarui informasi portofolio atau menambahkan banyak proyek. Pada iterasi selanjutnya, saya ingin menambahkan fungsionalitas dinamis seperti database untuk menyimpan data proyek dan kemampuan untuk menambah atau mengubah proyek tanpa harus mengubah kode HTML secara langsung. Selain itu, saya juga ingin menambahkan fitur contact form yang dapat menerima dan menyimpan pesan dari pengunjung.


### Tugas 2

1. Ketika pengguna membuka halaman `/projects/`, permintaan pertama kali diterima oleh `portofolio/urls.py`. Berkas tersebut menggunakan `include("main.urls")` untuk meneruskan pencarian URL ke aplikasi `main`. Selanjutnya, `main/urls.py` mencocokkan path `projects/` dengan view `show_projects`. View tersebut mengambil seluruh data proyek melalui `Project.objects.all()` dari model `Project`, lalu memasukkannya ke dalam context dengan nama `project_list`. Context tersebut diteruskan ke template `projects.html`. Template kemudian menggunakan Django Template Language untuk melakukan perulangan terhadap `project_list` dan menghasilkan halaman HTML yang dikirimkan kembali ke browser. Jika tidak terdapat data proyek, bagian `{% empty %}` akan menampilkan pesan bahwa belum ada proyek yang ditambahkan.

2. Data proyek sebaiknya disimpan pada model karena model memisahkan data dari struktur tampilannya. Jika data ditulis langsung dalam template, setiap penambahan atau perubahan proyek mengharuskan pengembang mengedit HTML secara manual. Dengan menggunakan model, data dapat dikelola melalui database, sedangkan template hanya bertanggung jawab menampilkan data. Pendekatan ini membuat kode lebih mudah dipelihara, mengurangi duplikasi, dan memudahkan pengembangan fitur berikutnya, seperti form untuk menambahkan proyek, halaman detail, pencarian, atau filter berdasarkan kategori.

3. `makemigrations` berfungsi membuat berkas migrasi berdasarkan perubahan yang terdeteksi pada model, sedangkan `migrate` menerapkan instruksi dalam berkas migrasi tersebut ke struktur database. Sebagai contoh, ketika saya menambahkan model `Project` dengan field `title`, `description`, `category`, `year`, dan `project_url`, saya menjalankan `python manage.py makemigrations` untuk menghasilkan berkas migrasi baru. Setelah itu, saya menjalankan `python manage.py migrate` untuk membuat tabel Project pada database.


### AI Disclosure
Dalam pengerjaan Tugas 2, saya menggunakan ChatGPT sebagai alat bantu untuk memahami ketentuan tugas, menyusun urutan implementasi pola Model-View-Template, dan mengevaluasi rancangan unit test. Saya memberikan konteks berupa ketentuan tugas dan meminta bantuan AI untuk memberitahu apa saja yang perlu saya selesaikan. Saran AI digunakan sebagai referensi, kemudian saya menyesuaikan model Project, isi proyek, struktur template, navigasi, serta penjelasan reflektif dengan kebutuhan portofolio saya sendiri. Saya juga memverifikasi hasil implementasi dan pengujian halaman secara langsung melalui development server.






### Tugas 3

1. ModelForm digunakan karena dapat membuat form berdasarkan struktur field pada model Django. Dengan demikian, kita tidak perlu mendefinisikan ulang seluruh field dan validasinya secara manual. ModelForm juga menyediakan metode `save()` untuk menyimpan data yang valid. Pada proyek saya, `ExperienceForm` menggunakan model `Experience` untuk membuat form tambah dan edit pengalaman. Untuk mengedit data, saya memberikan `instance=experience` agar yang diperbarui adalah objek yang sudah ada, bukan membuat objek baru.

`{% csrf_token %}` perlu ditambahkan pada form POST untuk membantu mencegah Cross-Site Request Forgery (CSRF), yaitu serangan yang membuat browser pengguna mengirim permintaan yang tidak dikehendaki ke aplikasi. Django memeriksa token yang dikirim bersama form untuk memvalidasi permintaan tersebut. Pada proyek saya, token ini digunakan pada form create, update, dan delete Experience. CSRF token tidak menggantikan autentikasi atau pemeriksaan hak akses.

2. JSON lebih sering digunakan dalam aplikasi web modern karena formatnya ringkas dan mudah diproses. JSON merepresentasikan data melalui pasangan key-value dan array, sehingga cocok dengan struktur data yang umum digunakan dalam aplikasi. Dibandingkan XML yang menggunakan tag pembuka dan penutup, JSON biasanya membutuhkan lebih sedikit karakter untuk menyampaikan data serupa.

JSON juga mudah digunakan dengan JavaScript melalui `JSON.parse()` dan `JSON.stringify()`, serta didukung oleh banyak bahasa pemrograman lainnya. Meskipun demikian, XML tetap berguna untuk kebutuhan tertentu, misalnya sistem yang menggunakan skema dan struktur dokumen XML.

3. Ketika pengguna mengakses `/api/experiences/`, Django mencocokkan URL tersebut dengan route pada `main/urls.py`, kemudian menjalankan fungsi `get_experiences_json`. Fungsi ini mengambil data Experience dari database melalui ORM dan menghasilkan QuerySet. Selanjutnya, `serializers.serialize("json", experiences)` mengubah data tersebut menjadi teks JSON. Hasilnya dikembalikan melalui `HttpResponse` dengan content type `application/json`.

Serialization diperlukan karena QuerySet dan instance model merupakan objek Python, bukan data JSON yang dapat langsung dipertukarkan dengan client. Serialization mengubahnya menjadi representasi yang dapat dikirim melalui HTTP dan diproses oleh penerima. Serializer Django menyertakan nama model, primary key, dan nilai field setiap objek.

Untuk menampilkan Experience pada halaman web, fungsi `show_experience` memanggil `get_experiences_json` secara langsung, membaca isi respons, kemudian melakukan deserialisasi menggunakan `serializers.deserialize`. Objek Experience diambil melalui `item.object` dan dimasukkan ke context sebagai `experience_list`. Template `experience.html` kemudian melakukan perulangan terhadap daftar tersebut untuk menampilkan data.


### AI DISCLOSURE TUGAS 3
Saya menggunakan ChatGPT untuk memahami konsep, memperoleh panduan dan contoh kode, membantu debugging. Implementasi dan pengujian saya lakukan sendiri.


### Tugas 4

1. **Autentikasi dan otorisasi.** Autentikasi memeriksa identitas pengguna melalui login, sedangkan otorisasi menentukan tindakan yang diizinkan setelah identitas diketahui. `portfolio_permission_required` mengarahkan pengunjung ke login dan menghasilkan HTTP 403 untuk akun yang tidak memiliki izin. Pemeriksaan dijalankan sebelum membaca/mengubah objek yang dilindungi. Menyembunyikan tombol hanya membantu tampilan; pembatasan utama tetap berada di server.

2. **Peran Editor.** Editor adalah anggota Django Group dengan nama persis `Editor`. Pemilik membuat grup dan menetapkan anggotanya melalui Django Admin. Editor boleh mengedit Experience dan Projects, tetapi tidak boleh menambah atau menghapusnya. Registrasi hanya membuat akun biasa dan tidak menerima pengaturan `groups`, `is_staff`, atau `is_superuser`.

3. **Star dan keamanan data.** `Experience.starred_by` merupakan `ManyToManyField` ke `settings.AUTH_USER_MODEL`. Tabel penghubung menjaga satu pasangan pengguna–Experience, sehingga satu pengguna tidak bisa mempunyai dua star pada Experience yang sama. View star hanya menerima POST dengan CSRF dan menggunakan `request.user`; pengguna tidak bisa memilih akun lain sebagai pemberi star. JSON hanya memuat daftar field portofolio yang diizinkan. Jumlah star dan status pengguna dihitung dengan `Count` dan `Exists`, tanpa menampilkan identitas akun lain.

4. **Session dan cookie.** Login menggunakan autentikasi Django serta cookie `last_login` untuk informasi waktu masuk. Cookie tersebut bukan bukti otorisasi; izin ditentukan dari pengguna yang diautentikasi melalui session. Tujuan `next` divalidasi agar login tidak mengarahkan pengguna ke situs luar. Logout memakai POST dengan CSRF, mengakhiri session, dan menghapus cookie `last_login`.

Catatan: saat instruksi Tugas 4 diperiksa pada 28 September 2026, bagian pertanyaan reflektif masih berupa placeholder. Poin bernomor di atas merupakan penjelasan implementasi, bukan jawaban atas pertanyaan dosen yang belum dipublikasikan.

#### Matriks hak akses

Aturan ini berlaku untuk Experience dan Projects. Detail Experience serta daftar kedua bagian tetap dapat dibaca tanpa login.

| Tindakan | Pengunjung | Pengguna biasa | Editor | Superuser |
|---|---|---|---|---|
| Membaca data dan JSON | Boleh | Boleh | Boleh | Boleh |
| Star/unstar | Diarahkan ke login | Boleh | Boleh | Boleh |
| Menambah | Diarahkan ke login | 403 | 403 | Boleh |
| Mengedit | Diarahkan ke login | 403 | Boleh | Boleh |
| Menghapus | Diarahkan ke login | 403 | 403 | Boleh |

Star, hapus, dan logout tidak menerima GET untuk mengubah data. Pengguna yang memiliki izin akan mendapat 405 jika memakai GET pada endpoint POST tersebut. Permintaan POST tanpa token CSRF yang valid ditolak oleh middleware Django dengan 403, termasuk sebelum pemeriksaan login pada view.

#### Mengatur Editor melalui Django Admin, langkah demi langkah

1. Jalankan migrasi dan buat superuser melalui perintah setup di atas. Jika sudah memiliki superuser, gunakan akun tersebut.
2. Buka `/register/` untuk membuat akun pengguna biasa yang nantinya akan menjadi Editor.
3. Login ke `/admin/` sebagai superuser.
4. Pada **Authentication and Authorization → Groups**, pilih **Add**.
5. Isi **Name** dengan `Editor`, termasuk huruf E kapital. Simpan. Tidak perlu memilih permissions tambahan karena view memeriksa nama grup secara langsung.
6. Buka **Users**, pilih akun yang akan menjadi Editor.
7. Pada bagian **Groups**, pindahkan `Editor` dari **Available groups** ke **Chosen groups**, kemudian **Save**.
8. Biarkan **Staff status** dan **Superuser status** tidak dicentang untuk Editor. Editor bekerja melalui form portofolio, bukan halaman administrasi.
9. Logout dari akun pemilik, lalu login melalui `/login/` sebagai Editor. Tombol Edit tampil pada Experience dan Projects; tombol Add dan Delete tidak tampil.
10. Untuk mencabut hak edit, kembali ke Admin sebagai pemilik, hapus keanggotaan grup Editor dari akun tersebut, lalu simpan.

Grup dan keanggotaannya adalah data database, sehingga perlu disiapkan pada setiap lingkungan yang ingin digunakan. Tidak ada akun atau grup istimewa yang otomatis dibuat oleh registrasi maupun migrasi.

#### Urutan implementasi

1. Menambahkan `main/permissions.py` untuk pemeriksaan superuser dan grup Editor; menerapkannya pada view create/update/delete Experience serta kondisi tombol pada template.
2. Menambahkan relasi `starred_by` pada Experience dan migrasi `0006_experience_starred_by`, kemudian menjalankan `migrate`.
3. Menambahkan endpoint `experience/<uuid>/star/` dengan login, POST, dan CSRF; membuat komponen tombol star serta halaman detail publik.
4. Membatasi serializer Experience dan Projects pada field publik. Format JSON Tugas 3 (`model`, `pk`, `fields`) dan pencarian Projects tetap dipertahankan. Halaman daftar tetap membaca hasil JSON dan melakukan deserialisasi; status star ditambahkan secara terpisah untuk tampilan.
5. Menyamakan pemeriksaan izin Projects, menyediakan edit untuk Editor/pemilik, memvalidasi `next` saat login, dan mengganti logout menjadi form POST.
6. Memperbarui tes lama yang belum login saat melakukan aksi pemilik dan menambahkan tes peran, perubahan data, CSRF, star, kebocoran JSON, serta input tidak valid.
7. Memeriksa halaman melalui browser dengan database pengujian terpisah, lalu mendokumentasikan hasilnya.

#### Cara memverifikasi hasil

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py runserver
```

Penjelasan kode langkah demi langkah tersedia pada [panduan belajar Tugas 4](docs/panduan-belajar-tugas-4.md). Hasil pengujian dan skenario browser tercatat pada [catatan pengujian Tugas 4](docs/pengujian-tugas-4.md). Daftar file penting: `main/models.py`, `main/permissions.py`, `main/views.py`, `main/urls.py`, `main/tests.py`, serta template Experience dan Projects.

Untuk pengujian manual, gunakan satu akun pemilik, satu anggota Editor, dan satu akun biasa. Periksa tampilan tombol, coba buka URL edit langsung, beri/batalkan star, lalu buka JSON tanpa login. Semua akun biasa tetap boleh memberi star meskipun tidak memiliki izin mengedit portofolio.

#### Pengumpulan

Setelah seluruh commit tersimpan dan pengujian selesai, push ke GitHub. Tautan yang dikumpulkan di SCELE berbentuk `https://github.com/KhalishahNafisah/myportofolio/commit/<hash-commit-final>`, bukan hanya alamat repository. Repository harus dapat dibaca publik. Pengumpulan SCELE perlu dilakukan melalui akun mahasiswa.

### AI Disclosure Tugas 4

Saya menggunakan ChatGPT (melalui Codex) untuk membantu pengerjaan Tugas 4.
Bantuan AI mencakup memberi pemahaman dan membantu implementasi perubahan kode untuk pembatasan
hak akses Experience, peran Editor, fitur star/unstar, keamanan
endpoint JSON, pengujian otomatis, dan dokumentasi.

Alur prompting dilakukan bertahap: pemeriksaan kebutuhan tugas
dan kondisi proyek, penyusunan langkah pengerjaan untuk ditinjau,
kemudian implementasi, pengujian, dan evaluasi hasil.
Ringkasan prompting dan evaluasi keterbatasan AI dicatat pada
[log bantuan AI Tugas 4](docs/ai-log-tugas-4.md).
