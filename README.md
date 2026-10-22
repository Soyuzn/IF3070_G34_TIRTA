# IF3070 G34 TIRTA

Python 3.10+, Matplotlib, JSON, CSV.

## Folder

- `data/`: kendaraan dan kapal
- `src/`: algoritma, validasi, pencatatan, visualisasi
- `tests/`: tes program
- `output/`: hasil run dan gambar
- `docs/`: kontrak dan laporan

## Cara run

Buka terminal di root repo. Kalau belum ada `.venv`, buat sekali:

```sh
python3 -m venv .venv
```

Aktifkan lalu pasang kebutuhan program:

```sh
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

GA, satu run:

```sh
python3 -m src.genetic --jumlah-populasi 30 --batas-iterasi 30 --seed 40 \
  --output output/ga_01
```

HC dan SA lewat runner. Masing-masing menjalankan seed 40, 41, 42:

```sh
python3 -m src.eksperimen --modul src.hill_climbing --output output/hc_01 \
  --seed 40 41 42 --parameter '{"varian": "stochastic", "maks_gagal": 1000}'

python3 -m src.eksperimen --modul src.simulated_annealing --output output/sa_01 \
  --seed 40 41 42 --parameter '{"batas_iterasi": 1000}'
```

Untuk bonus HC, ganti `varian` menjadi `steepest`, `sideways`, atau `random_restart`.
Batas default sideways 100 langkah dengan nilai sama, restart 10 kali setelah pencarian pertama.
Bisa diubah lewat `maks_sideways` dan `maks_restart` di `--parameter`.

Ganti nama folder output tiap mengulang run. Hasil lama tidak ditimpa.
GA menyimpan hasil langsung di folder output, runner membuat subfolder per ulangan.
Isinya `hasil.json`, `riwayat.csv`, `state_awal.png`, `state_akhir.png`, dan `objektif.png`.
SA juga punya `penerimaan_sa.png` jika ada data eksponennya.
Runner menambah `ringkasan.csv` dan `ringkasan.md` di folder induk. PNG bisa dibuka langsung.

Tes program:

```sh
python3 -m unittest discover -s tests -v
```

## Data

30 kendaraan, satu kapal. Angkanya sintetis. Nilai objektif adalah total tarif kirim
kendaraan yang dimuat. Ukuran dalam sel grid, berat dan kapasitas dalam unit yang sama,
tarif dalam juta rupiah. ETA dalam hari, tetapi tidak masuk hitungan objektif.
Format state dan keluaran algoritma ada di [kontrak](docs/kontrak.md).

## Referensi

- Matplotlib: [dasar grafik](https://matplotlib.org/stable/users/explain/quick_start.html),
  [Rectangle](https://matplotlib.org/stable/api/_as_gen/matplotlib.patches.Rectangle.html),
  [simpan PNG](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.savefig.html).
- Python: [random dan seed](https://docs.python.org/3/library/random.html),
  [seleksi induk berbobot](https://docs.python.org/3/library/random.html#random.choices),
  [pengukuran durasi](https://docs.python.org/3/library/time.html#time.perf_counter).
- Russell dan Norvig, *Artificial Intelligence: A Modern Approach*, edisi 4,
  bagian 4.1.2, Figure 4.5, hlm. 115. Acuan SA; jadwal suhu dan bias diatur di kode.
