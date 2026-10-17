# Verifikasi Orang 2 — 15 Oktober 2026

Pemeriksaan dilakukan langsung di repo tujuan pada branch
`feat/visualisasi_data`. `git fetch origin` dilanjutkan dengan
`git pull --no-rebase --no-edit origin initial-datasets` menghasilkan
`Already up to date`; dasar implementasi tetap commit `546b19c`, sama dengan
`origin/initial-datasets`. Tidak ada konflik, commit, atau push dari sesi ini.
`data/` dan `docs/kontrak.md` tidak diubah.

## Hasil

- Python 3.14.7 dan Matplotlib 3.11.2 di `.venv`.
- `.venv/bin/python -m unittest discover -s tests -v`: 17 tes lulus,
  tanpa tes yang dilewati.
- `.venv/bin/python -m compileall -q src tests`: lulus.
- `git diff --check`: lulus.
- Demo grafik dataset wajib: lulus. Seed 42, 13 kendaraan dimuat, objective
  414 juta rupiah, seluruh state valid.
- Demo grafik multi-kapal: lulus. Seed 42, 19 kendaraan dimuat, objective total
  731 juta rupiah, kapasitas diperiksa per kapal.
- Setiap demo menghasilkan `hasil.json`, `riwayat.csv`, gambar state awal/akhir,
  grafik objective, grafik penerimaan SA, dan grafik populasi GA. Seluruh PNG
  berhasil dirender dan diperiksa secara visual: asal koordinat berada di kiri
  atas, sumbu y mengarah ke bawah, dimensi/orientasi sesuai kontrak, kendaraan
  tidak bertumpang tindih, sel kosong terlihat, daftar kendaraan di luar kapal
  terbaca, dan kurva SA/GA memiliki label serta seri yang benar.
- Kedua demo bertanda `ilustrasi=true`, state akhir sama dengan awal,
  `durasi_detik=0`, dan hanya memiliki iterasi 0 pada riwayat utama. Kurva SA/GA
  memakai angka buatan yang berlabel `ILUSTRASI`; semua keluaran bukan hasil
  algoritma pencarian.

Perintah verifikasi grafik yang dijalankan:

```sh
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m src.contoh --output output/validasi_grafik
.venv/bin/python -m src.contoh --kapal data/kapal_bonus.json --output output/validasi_grafik_multi
```

Direktori validasi tersebut diabaikan Git sesuai `.gitignore`. JSON/CSV demo
satu kapal sama persis dengan contoh yang disertakan di `output/ilustrasi_data/`.

Peninjauan lanjutan menyeragamkan istilah `data_kendaraan` dan `penempatan`,
menghapus buffer CSV sementara, dan memakai `set.isdisjoint` untuk memeriksa
tabrakan tanpa membuat hasil irisan. Kesalahan validasi yang menolak berat
atau kapasitas positif di bawah 1 sudah diperbaiki dan diberi tes regresi.
Demo ulang ada di `output/tinjauan_bahasa.D9lzWs/`: JSON/CSV dan kelima PNG
untuk setiap skenario identik dengan demo sebelum peninjauan. Demo tanpa
grafik juga berhasil memakai Python sistem tanpa Matplotlib.

Pengujian integrasi di `tests/test_integrasi.py` menjalankan demo CLI sesuai
README untuk satu dan beberapa kapal, memvalidasi snapshot dataset/state,
mencocokkan JSON/CSV dengan contoh repo, serta membaca kelima PNG tiap demo.
Populasi awal/akhir GA dan statistiknya juga diuji melalui penyimpanan JSON.
Ini pemeriksaan format integrasi menggunakan populasi ilustrasi.

Pemeriksaan tambahan: `pip check` lulus, seluruh tautan lokal Markdown valid,
dan inisialisasi untuk 100 seed pada masing-masing dataset kapal menghasilkan
state valid yang dapat diulang. Contoh di `output/ilustrasi_data/` tetap masuk
cakupan Git. Dengan Python sistem tanpa Matplotlib, 15 tes lulus dan 2 tes
grafik dilewati; modul data/pencatatan juga bisa diimpor dengan `python3 -S`.

Integrasi terverifikasi untuk seluruh file yang tersedia di working tree.
Implementasi HC, SA, dan GA belum ada di repo ini, sehingga pemanggilan dari
algoritma tersebut perlu diuji setelah modulnya tersedia.

## Perapian 16 Oktober 2026

Modul `src` diringkas dari 357 menjadi 345 baris dengan menggabungkan validasi
atribut dan merapikan alur demo. Gambar state memakai label ID serta orientasi
langsung pada kendaraan. Dependensi dan antarmuka fungsi tetap sama.

Seluruh 17 tes dan pemeriksaan sintaks lulus. State untuk seed 0–99 pada kedua
dataset kapal identik dengan sebelum perapian. Demo grafik tersimpan di
`output/validasi_ringkas.tipV9U/`; gambar satu dan multi-kapal sudah diperiksa
secara visual. Demo tanpa grafik juga berhasil dengan Python sistem.

Keputusan algoritma dan eksperimen yang masih terbuka tercatat di
`docs/integrasi_orang2.md`. Tidak ada perbedaan kontrak terhadap batasan wajib
spesifikasi; objective bonus masih usulan tim dan tidak dicampurkan di sini.
