# IF3070 G34 — TIRTA

Penataan kendaraan pada geladak kapal untuk memaksimalkan jumlah `tarif_kirim`.
Kontrak tim ada di [docs/kontrak.md](docs/kontrak.md).

## Menjalankan utilitas Orang 2

Python 3.10 atau lebih baru. Jalankan dari direktori utama repo:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.contoh
python -m unittest discover -s tests -v
```

Tes mencakup validasi data/state, pencatatan, visualisasi, dan integrasi demo
CLI dengan dataset serta contoh keluaran repo.

Demo membuat `output/ilustrasi/`: JSON, CSV, gambar state awal/akhir, grafik
objektif, serta contoh grafik SA dan GA. Semuanya **ilustrasi**, bukan hasil
pencarian. State akhir sama dengan awal dan durasi pencarian nol.
Folder tujuan harus baru; gunakan `--output output/ilustrasi_2` untuk mengulang.

Tanpa Matplotlib, data dan pencatatan tetap bisa dipakai:

```sh
python -m src.contoh --tanpa-grafik --output output/ilustrasi_data_baru
python -m src.contoh --kapal data/kapal_bonus.json --tanpa-grafik --output output/ilustrasi_multi
```

## Struktur dan pembagian

- `data/`, `docs/kontrak.md`: dataset dan kontrak bersama dari `initial-datasets`.
- `src/data.py`: baca data, validasi, objective wajib, inisialisasi berseed.
- `src/pencatatan.py`: timer pencarian dan ekspor JSON/CSV.
- `src/visualisasi.py`: gambar grid, kurva objektif/populasi, kurva penerimaan SA.
- `src/contoh.py`: demo tanpa algoritma.
- `tests/`: pengujian kontrak dan utilitas.
- `output/`: hasil lokal, diabaikan Git kecuali `.gitkeep` dan contoh di bawah.

`output/ilustrasi_data/` juga disertakan sebagai contoh JSON/CSV berlabel
ilustrasi dari dataset tim, seed 42. Hasil ini hanya inisialisasi, bukan optimasi.

Orang 2 menyiapkan utilitas eksperimen dan visualisasi. Pembagian implementasi
algoritma diisi tim; modul ini tidak berisi pencarian atau fungsi tetangga.
Petunjuk pemakaian ada di [docs/integrasi_orang2.md](docs/integrasi_orang2.md).
Gunakan [template analisis](docs/template_analisis.md) setelah percobaan nyata.
Laporan akhir tetap perlu dibuat sebagai PDF di `docs/`, beserta lampiran
penggunaan Generative AI sesuai spesifikasi tugas.
