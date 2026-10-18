# IF3070 G34 TIRTA

## Tech stack

Python 3.10+, JSON, Matplotlib. Selain Matplotlib, modul yang dipakai bawaan
Python. Sumber belajarnya ada di [referensi](docs/referensi.md).

## Struktur

- `data/`: 30 kendaraan, skenario satu kapal dan dua kapal
- `src/`: baca data, inisialisasi, validasi, pencatatan, visualisasi
- `tests/`: tes utilitas bersama
- `output/`: hasil run
- `docs/`: kontrak, cara integrasi, template analisis, dan laporan

## Jalankan

Jalankan dari direktori utama repo:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.contoh
python -m unittest discover -s tests -v
```

Contoh membuat JSON, CSV, dan PNG di `output/ilustrasi/`. Ini baru state acak
dan contoh grafik, belum hasil HC/SA/GA. Pakai folder baru untuk run berikutnya:

```sh
python -m src.contoh --kapal data/kapal_bonus.json --objektif tarif_eta \
  --output output/ilustrasi_eta
```

## Kontrak dan satuan

State memuat semua ID kendaraan. `None` berarti di luar kapal; kendaraan yang
dimuat punya `kapal_id`, `x`, `y`, `orientasi`. Titik asal di kiri atas dek.
Ukuran dalam sel grid, berat/kapasitas dalam unit yang sama, tarif dalam juta
rupiah, ETA dalam sisa hari. Semua angka dataset sintetis.

Objective wajib menjumlahkan `tarif_kirim` yang dimuat. Bonus `tarif_eta`
menjumlahkan `tarif_kirim / (1 + eta_hari)`. Lihat [kontrak](docs/kontrak.md)
dan [cara menyambungkan algoritma](docs/integrasi.md) sebelum mulai.
