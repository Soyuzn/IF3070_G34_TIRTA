# Pemakaian bersama

HC, SA, dan GA memakai list `kapal`, list `kendaraan`, dan dict `state`
sesuai [kontrak](kontrak.md). Tidak perlu membuat format data baru.

```python
from src.data import baca_data, inisialisasi_acak, nilai_objektif

kapal, kendaraan = baca_data()
awal = inisialisasi_acak(kapal, kendaraan, seed=42)
objektif = "tarif_kirim"
nilai = nilai_objektif(kapal, kendaraan, awal, objektif)
```

Untuk multi-kapal, gunakan `baca_data("data/kapal_bonus.json")`.
Objective default adalah `tarif_kirim`; bonus memakai `objektif="tarif_eta"`.
Gunakan pilihan yang sama pada algoritma, pencatatan, dan gambar.

## Sambungan algoritma

Setiap modul algoritma nanti menyediakan fungsi:

```python
cari(kapal, kendaraan, state_awal, seed, objektif="tarif_kirim", **parameter)
```

Hasilnya tuple `(state_akhir, riwayat, metrik)`. `state_akhir` adalah state
terbaik yang valid; `metrik` berupa dict untuk statistik khusus algoritma.
Di dalam algoritma, pakai `random.Random(seed)` dan salin state sebelum
mengubahnya. Jangan mengubah dataset atau state awal milik pemanggil.

Timer hanya membungkus pencarian. Membaca data, inisialisasi, dan menggambar
dilakukan di luar timer:

```python
from copy import deepcopy
from src.pencatatan import ukur_pencarian, simpan_percobaan

hasil, durasi = ukur_pencarian(
    cari, kapal, kendaraan, deepcopy(awal), seed=42, objektif=objektif,
)
akhir, riwayat, metrik = hasil
simpan_percobaan(
    "output/hc_42", algoritma="hc", seed=42, parameter={},
    kapal=kapal, kendaraan=kendaraan, state_awal=awal, state_akhir=akhir,
    durasi_detik=durasi, riwayat=riwayat, metrik=metrik, objektif=objektif,
)
```

`cari` pada contoh diimpor dari modul algoritma masing-masing. Fungsi itu
belum disediakan di tahap prasyarat. Folder keluaran harus baru agar hasil
run sebelumnya tidak tertimpa.

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

`gambar_state`, `gambar_riwayat`, dan `gambar_penerimaan` di `src.visualisasi`
mengembalikan Figure Matplotlib. Simpan dengan `fig.savefig(...)`, lalu
`plt.close(fig)`. Contoh lengkap yang sudah bisa dijalankan ada di `src.contoh`.
