# Pemakaian bersama

HC, SA, dan GA memakai list `kapal`, list `kendaraan`, dan dict `state`
sesuai [kontrak](kontrak.md). Tidak perlu membuat format data baru.

```python
from src.data import baca_data, inisialisasi_acak, nilai_objektif

kapal, kendaraan = baca_data()
awal = inisialisasi_acak(kapal, kendaraan, seed=42)
nilai = nilai_objektif(kapal, kendaraan, awal)
```

List `kapal` harus berisi tepat satu kapal.
Objective adalah total tarif kirim kendaraan yang dimuat, dalam juta rupiah.

## Sambungan algoritma

Setiap modul algoritma nanti menyediakan fungsi:

```python
cari(kapal, kendaraan, state_awal, seed, **parameter)
```

Hasilnya tuple `(state_akhir, riwayat, metrik)`. `state_akhir` adalah state
terbaik yang valid; `metrik` berupa dict untuk statistik khusus algoritma.
Di dalam algoritma, pakai `random.Random(seed)` dan salin state sebelum
mengubahnya. Jangan mengubah dataset atau state awal milik pemanggil.

Timer membungkus pencarian. Membaca data, membuat state acak pertama, dan
menggambar dilakukan di luar timer. Pada GA, pembentukan populasi masuk timer:

```python
from copy import deepcopy
from src.pencatatan import ukur_pencarian, simpan_percobaan
from src.visualisasi import simpan_gambar

hasil, durasi = ukur_pencarian(
    cari, kapal, kendaraan, deepcopy(awal), seed=42,
)
akhir, riwayat, metrik = hasil
tujuan = simpan_percobaan(
    "output/hc_42", algoritma="hc", seed=42, parameter={},
    kapal=kapal, kendaraan=kendaraan, state_awal=awal, state_akhir=akhir,
    durasi_detik=durasi, riwayat=riwayat, metrik=metrik,
)
simpan_gambar(tujuan)
```

`cari` pada contoh diimpor dari modul algoritma masing-masing. GA ada di
`src.genetic`, SA di `src.simulated_annealing`; HC belum digabung. Folder keluaran harus baru agar
hasil run sebelumnya tidak tertimpa.

## Genetika

Implementasi GA ada di `src/genetic.py`, memakai satu kapal dan total tarif kirim.

`src.genetic.cari` menerima `jumlah_populasi` (minimal 2), `batas_iterasi`
(boleh 0), dan `peluang_mutasi` (0 sampai 1, default 0.2).

- Satu individu adalah satu state. Urutan gen mengikuti daftar kendaraan.
- Populasi awal berisi salinan state masukan dan state acak lainnya.
- Fitness adalah total tarif kirim. Peluang induk = fitness / total fitness populasi.
  Jika semua nol, pilih merata. Induk yang sama boleh terpilih dua kali.
- Kawin silang satu titik menghasilkan dua anak. Gen menyimpan penempatan atau `None`.
- Perbaikan mengecek gen dalam urutan acak. Penempatan yang melanggar batasan
  dikembalikan ke luar kapal (`None`). Tidak ada kendaraan yang dihapus dari state.
- Peluang mutasi berlaku per anak. Mutasi memilih satu kendaraan, lalu memilih
  penempatan valid lain atau mengeluarkannya. Jika tidak ada pilihan, tetap sama.
- Satu individu terbaik disalin ke generasi berikutnya (elitisme).

Riwayat mencakup generasi 0 sampai `batas_iterasi`. `state_akhir` adalah individu
terbaik generasi terakhir. CLI menyimpan individu terbaik populasi awal sebagai
`state_awal`, sehingga sesuai statistik generasi 0. Kedua populasi utuh ada di
`metrik`.

## Simulated annealing

SA memakai `tetangga_acak(kapal, kendaraan, state, acak)` dari `src/tetangga.py`.
Hasilnya `(state_baru, langkah)` atau `None` bila sampling gagal. Langkahnya
pindah, putar, atau tukar; kandidat tetap harus memenuhi semua batasan kapal.
Sampling gagal tidak otomatis berarti local optimum.

Default: `suhu_awal=50`, `pendinginan=0.995`, `suhu_minimum=0.1`,
`batas_iterasi=1000`, `evaluation_bias=1`, `interval_stuck=50`.
Suhu iterasi ke-i adalah `suhu_awal * pendinginan ** (i - 1)`.
Berhenti saat batas iterasi tercapai atau suhu di bawah minimum.

Nilai sama atau lebih baik selalu diterima. Jika turun, peluang penerimaannya
`exp((delta / suhu) * evaluation_bias)`. Bias harus positif; nilai di atas 1
membuat penurunan lebih sulit diterima. Ini pilihan implementasi SA dan tidak
mengubah fitness. Grafik tetap memakai nilai mentah `exp(delta / suhu)`.
Sumbu grafik eksponen memakai skala symlog agar nilai besar tetap terbaca.
Eksponen yang meluap disimpan `None` dan dihitung dalam metrik.

`frekuensi_stuck` adalah jumlah checkpoint stuck dibagi jumlah checkpoint.
Pemeriksaan dilakukan tiap `interval_stuck` dan pada iterasi terakhir.
Stuck berarti tidak ada satu langkah valid yang langsung menaikkan tarif;
plateau termasuk. Ini bukan jumlah run yang gagal atau bukti optimum global.

## Runner eksperimen

`src/eksperimen.py` menjalankan satu konfigurasi untuk beberapa seed.
Parameter algoritma ditulis sebagai JSON; nama kuncinya sama dengan argumen `cari`:

```sh
python3 -m src.eksperimen --modul src.genetic --output output/ga_ulangan_01 \
  --seed 40 41 42 --parameter '{"jumlah_populasi": 20, "batas_iterasi": 100}'
```

Untuk SA, ganti modul dengan `src.simulated_annealing` dan gunakan parameter SA.
Tiap seed disimpan dalam `ulangan_N_seed_S/`; ringkasan CSV dan Markdown berada
di folder induk. `--tanpa-grafik` menyimpan data saja.
Runner mengikuti pemilihan state awal GA di atas dan mencatat parameter efektif,
termasuk default. Satu pemanggilan hanya menguji satu konfigurasi, jadi variasi
jumlah populasi atau batas iterasi dijalankan terpisah dengan folder baru.

## Riwayat dan gambar

Riwayat berupa list dict. Indeks `iterasi` dimulai dari 0 dan terus naik,
termasuk saat restart. Untuk GA, satu generasi dihitung satu iterasi.

| Kolom | Isi |
| --- | --- |
| `iterasi` | Indeks iterasi |
| `objektif` | Nilai state saat ini untuk HC/SA |
| `maksimum_populasi`, `rata_rata_populasi` | Keduanya diisi untuk GA |
| `eksponen_penerimaan` | Nilai mentah `exp(ΔE/T)` SA, boleh lebih dari 1 |
| `restart` | Indeks restart; 0 untuk pencarian pertama |

Setiap baris punya `objektif` atau kedua statistik populasi. Kolom yang tidak
dipakai boleh dihilangkan. Untuk SA, `ΔE = nilai_kandidat - nilai_saat_ini`.
Nilai state saat ini boleh turun dan berbeda dari state terbaik yang dikembalikan.

Simpan statistik tambahan di `metrik`: jumlah restart dan iterasi per restart
untuk HC, frekuensi stuck beserta definisinya untuk SA, serta populasi
awal/akhir untuk GA. State awal/akhir GA memakai individu terbaik populasi itu.

Visualisasi ada di `src/visualisasi.py`, memakai Matplotlib. Panggil
`simpan_gambar(tujuan)` setelah `simpan_percobaan` selesai. CLI GA dan runner melakukan ini.
Hasilnya `state_awal.png`, `state_akhir.png`, dan `objektif.png` dalam folder run.
Jika ada data penerimaan SA, dibuat juga `penerimaan_sa.png`. Gambar dibuat
di luar timer pencarian. JSON dan CSV tetap menyimpan data lengkap percobaan.

Hasil JSON mencantumkan objective `jumlah tarif_kirim` dan satuan `juta rupiah`.
