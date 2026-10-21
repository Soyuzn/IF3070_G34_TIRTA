# IF3070 G34 TIRTA

## Tech stack

Python 3.10+, JSON, CSV, dan Matplotlib untuk gambar.
Sumber belajarnya ada di [referensi](docs/referensi.md).

## Struktur

- `data/`: 30 kendaraan dan data kapal
- `src/`: data, tetangga, GA, SA, eksperimen, pencatatan, dan visualisasi
- `tests/`: tes utilitas dan algoritma
- `output/`: hasil run
- `docs/`: kontrak, cara integrasi, template analisis, dan laporan

## Jalankan

Jalankan dari direktori utama repo:

```sh
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m src.genetic --jumlah-populasi 20 --batas-iterasi 10 --seed 1 \
  --output output/ga_satu_01
```

Jika belum punya `.venv`, buat dahulu dengan `python3 -m venv .venv`.
Program memakai satu kapal dari `data/kapal.json` dan fitness total tarif kirim.
Gunakan folder `--output` baru untuk tiap run. `--seed` default 42.

Hasil ada di `output/ga_satu_01/`: `hasil.json`, `riwayat.csv`, `state_awal.png`,
`state_akhir.png`, dan `objektif.png`. Buka PNG langsung dari Finder.
`src/visualisasi.py` menggambar posisi kendaraan dan grafik memakai Matplotlib.

SA lewat runner eksperimen, tiga ulangan dengan seed 40, 41, 42:

```sh
python3 -m src.eksperimen --modul src.simulated_annealing --output output/sa_01 \
  --parameter '{"batas_iterasi": 1000, "evaluation_bias": 1}'
```

Tiap ulangan punya JSON, CSV, dan PNG, termasuk `penerimaan_sa.png` jika ada
data eksponennya. `ringkasan.csv` dan `ringkasan.md` merangkum seluruh ulangan.
Runner juga bisa memakai `--modul src.genetic`; rinciannya di [integrasi](docs/integrasi.md).

Tes otomatis:

```sh
python3 -m unittest discover -s tests -v
```

Tes memakai folder sementara dan tidak menambah hasil ke `output/`.

## Kontrak dan satuan

State memuat semua ID kendaraan. `None` berarti di luar kapal; kendaraan yang
dimuat punya `kapal_id`, `x`, `y`, `orientasi`. Titik asal di kiri atas dek.
Ukuran dalam sel grid, berat/kapasitas dalam unit yang sama, tarif dalam juta
rupiah, ETA dalam sisa hari. Semua angka dataset sintetis.

Fitness menjumlahkan `tarif_kirim` kendaraan yang dimuat. Lihat [kontrak](docs/kontrak.md)
dan [cara menyambungkan algoritma](docs/integrasi.md) sebelum mulai.
`eta_hari` tetap ada pada dataset dan tidak digunakan dalam perhitungan fitness.
