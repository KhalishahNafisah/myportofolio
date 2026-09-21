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
