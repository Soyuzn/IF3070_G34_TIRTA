# Integrasi utilitas Orang 2

Mengikuti `docs/kontrak.md` dari commit `546b19c` (`initial-datasets`).
Dataset dan kontrak tersebut tidak diubah. Tidak ada kelas domain tambahan:
semua fungsi memakai list/dict yang sama dengan JSON tim.
`state` berarti keadaan seluruh kendaraan, termasuk yang tidak diangkut.
Istilah di kode mengikuti kontrak: `data_kendaraan` untuk satu kendaraan,
`penempatan` untuk kapal, koordinat, dan orientasinya, serta `dek` untuk area
kapal. Dependensi eksternal hanya Matplotlib; modul lain bawaan Python.

## Bentuk data

| Data | Bentuk dan atribut |
|---|---|
| `kapal` | List dict: `id`, `lebar`, `panjang`, `kapasitas` |
| `kendaraan` | List dict: `id`, `lebar`, `panjang`, `tarif_kirim`, `berat`, `eta_hari` |
| `state` | Dict dengan tepat satu entri untuk setiap `id` kendaraan |
| Penempatan | `{"kapal_id": "kapal_utama", "x": 0, "y": 0, "orientasi": "vertikal"}` |
| Di luar kapal | `None` di Python; `null` di JSON. Tidak ada koordinat/orientasi untuk entri ini. |

`(x, y)` adalah sudut kiri atas. Sumbu `x` ke kanan, `y` ke bawah.
`vertikal`: lebar pada sumbu x, panjang pada sumbu y; `horizontal`: ditukar.
Label kendaraan pada gambar memuat ID dan orientasi sesuai kontrak.
Warna mengikuti urutan `kendaraan`; pertahankan urutan dataset antar gambar.
Sel kosong terlihat melalui grid dek, sedangkan kendaraan di luar disebutkan
dalam daftar di bawah gambar.

Tarif dalam juta rupiah, ukuran/koordinat dalam sel grid, berat/kapasitas dalam
unit yang sama. `eta_hari` adalah sisa hari dan tidak masuk objective wajib.
`nilai_objektif` menjumlahkan `tarif_kirim` yang dimuat, setelah validasi.
Usulan objective bonus di kontrak belum diimplementasikan di utilitas ini.

## Memulai dan memeriksa state

```python
from src.data import baca_data, inisialisasi_acak, periksa_state, nilai_objektif

kapal, kendaraan = baca_data()
state_awal = inisialisasi_acak(kapal, kendaraan, seed=42)
periksa_state(kapal, kendaraan, state_awal)  # ValueError bila tidak valid
objektif_awal = nilai_objektif(kapal, kendaraan, state_awal)
```

Inisialisasi mengacak urutan kendaraan, lalu memilih satu penempatan layak
atau `None` untuk setiap kendaraan. RNG lokal tidak mengubah RNG global.
Seed dan urutan input yang sama menghasilkan state yang sama. Ini bukan
sampling seragam dari seluruh state valid; tidak menilai tarif atau mencari
perbaikan. Simpan state awal saat eksperimen agar hasil dapat dibandingkan.

Validasi menolak ID berulang, atribut yang menyimpang dari kontrak, dimensi
bukan integer positif, angka tidak berhingga, berat/kapasitas tidak positif,
tarif negatif, dan `eta_hari` bukan integer nonnegatif. Pemeriksaan state
mencakup kelengkapan ID, `kapal_id`, orientasi, koordinat integer, seluruh
batas kendaraan, tumpang tindih, serta kapasitas **per kapal**. `baca_json`
menolak kunci JSON berulang sebelum dict terbentuk. Pemanggil yang membaca
JSON sendiri perlu melakukan hal yang sama; dict tidak menyimpan kunci ganda.

## Batas waktu pencarian

`ukur_pencarian(fungsi, *args, **kwargs)` mengembalikan `(hasil, durasi_detik)`
dengan `time.perf_counter`. Hanya panggil fungsi pencarian di dalamnya:

```python
from copy import deepcopy
from src.pencatatan import ukur_pencarian

# jalankan_algoritma disediakan anggota algoritma, bukan utilitas Orang 2.
state_kerja = deepcopy(state_awal)
hasil, durasi_detik = ukur_pencarian(jalankan_algoritma, state_kerja)
```

Salin state awal sebelum algoritma mengubahnya. Pembacaan dataset dan
inisialisasi dilakukan sebelum timer; serialisasi, penyimpanan, dan plotting
sesudah timer. Evaluasi dan pencatatan riwayat dalam loop tetap termasuk
proses pencarian. Anggota algoritma mengatur RNG dan seed pencariannya sendiri.
Jika berbeda, simpan seed pencarian di `parameter` dan seed inisialisasi di `seed`.

## Satu baris riwayat

`riwayat` adalah list dict. Baris pertama `iterasi=0`; baris berikutnya
memakai indeks global yang meningkat, termasuk saat restart. Catat tiap iterasi
yang dilewati; untuk GA satu generasi dihitung satu iterasi. `jumlah_iterasi`
di JSON diambil dari indeks terakhir, bukan jumlah baris.

| Kolom | Isi |
|---|---|
| `iterasi` | Integer nonnegatif, 0 untuk kondisi awal |
| `objektif` | Nilai state saat ini setelah satu iterasi; SA boleh turun |
| `maksimum_populasi` | Nilai maksimum objective populasi GA |
| `rata_rata_populasi` | Rata-rata objective seluruh populasi GA; berpasangan dengan maksimum |
| `eksponen_penerimaan` | Nilai mentah `exp(ΔE/T)` kandidat SA pada iterasi itu; boleh >1 |
| `restart` | Nomor restart, 0 untuk pencarian pertama |

Setiap baris berisi `objektif` atau kedua statistik populasi. Kolom opsional
boleh dihilangkan/`None`; CSV menulisnya kosong, bukan nol palsu. Semua angka
harus berhingga dan nonnegatif. Pada iterasi 0 biasanya belum ada kandidat SA,
jadi kosongkan `eksponen_penerimaan`. Tetapkan `ΔE = nilai_kandidat - nilai_saat_ini`
untuk maksimisasi. Jangan memasukkan probabilitas yang telah dibatasi ke 1.

`state_akhir` adalah solusi yang dikembalikan algoritma. Bila algoritma
mengembalikan state terbaik sepanjang pencarian, nilainya bisa berbeda dari
baris terakhir state saat ini. Jelaskan kebijakan pengembalian di `parameter`.
Untuk GA, gunakan individu terbaik sebagai state awal/akhir representatif.
Simpan seluruh populasi sebagai list state dalam `metrik["populasi_awal"]`
dan `metrik["populasi_akhir"]` agar populasi tidak hilang dari catatan.

## Menyimpan dan menggambar

```python
from src.pencatatan import simpan_percobaan
from src.visualisasi import gambar_state, gambar_riwayat
import matplotlib.pyplot as plt

tujuan = simpan_percobaan(
    "output/hc_konfigurasi1_ulangan1", algoritma="hill_climbing",
    seed=42, parameter={"varian": "isi sesuai implementasi"},
    kapal=kapal, kendaraan=kendaraan, state_awal=state_awal,
    state_akhir=state_akhir, durasi_detik=durasi_detik,
    riwayat=riwayat, metrik={},
)
fig = gambar_state(kapal, kendaraan, state_akhir, "Keadaan akhir")
fig.savefig(tujuan / "state_akhir.png", dpi=150)
plt.close(fig)
fig = gambar_riwayat(riwayat)
fig.savefig(tujuan / "objektif.png", dpi=150)
plt.close(fig)
```

`hasil.json` memuat snapshot dataset, kedua state, objective awal/akhir,
durasi dalam detik, seed, parameter, metrik, riwayat, dan penanda `ilustrasi`.
`riwayat.csv` memuat baris yang sama untuk diolah lagi. Tujuan yang sudah ada
ditolak agar percobaan tidak tertimpa. `ilustrasi=True` wajib untuk data buatan.
Parameter dan metrik harus berupa dict berisi nilai yang dapat ditulis ke JSON.
Pemeriksaan format tidak menjamin kelengkapan laporan tiap algoritma;
pemanggil tetap mengisi parameter dan metrik berikut.

| Algoritma | Isi `parameter` | Isi `metrik` / riwayat tambahan |
|---|---|---|
| Hill Climbing | `varian`, kriteria berhenti; `maximum_sideways_move` atau `maximum_restart` bila berlaku | `jumlah_restart`, `iterasi_per_restart` untuk random restart; indeks akhir untuk iterasi berhenti |
| SA | Suhu awal, jadwal suhu, kriteria berhenti, definisi stuck | `frekuensi_stuck`; `eksponen_penerimaan` di riwayat |
| GA | `jumlah_populasi`, `batas_iterasi`, parameter seleksi/mutasi/crossover yang benar-benar dipakai | Seluruh populasi awal/akhir, statistik maksimum dan rata-rata per generasi |

Grafik tambahan wajib: `gambar_penerimaan(riwayat)` untuk SA;
`gambar_riwayat(riwayat)` menggambar kedua statistik bila diberi riwayat GA.
Semua fungsi gambar mengembalikan Figure; pemanggil menutupnya sesudah simpan.

## Kesesuaian spesifikasi dan keputusan tim

Kontrak sesuai batasan wajib: pemetaan semua kendaraan, grid integer,
kendaraan sepenuhnya di luar, batas dek, tanpa tumpang tindih, kapasitas,
dan jumlah tarif. Kalimat soal yang menyebut truk/paket/peti kemas dibaca
sebagai kendaraan/kapal sesuai entitas dan kontrak; representasi tidak diubah.

Yang masih perlu ditetapkan sebelum eksperimen:

- Varian Hill Climbing, kriteria berhenti, batas sideways/restart bila dipakai.
- Definisi dan satuan `frekuensi_stuck` SA (hitungan kejadian atau proporsi),
  serta cara mendeteksi kejadian. Jangan menyamakan keduanya dalam tabel.
- Parameter setiap algoritma dan daftar seed/ulangan. Untuk GA: 3 variasi
  batas iterasi dengan populasi tetap, lalu 3 variasi populasi dengan batas
  iterasi tetap; masing-masing konfigurasi 3 ulangan. HC dan SA juga 3 ulangan.
- Penerapan objective bonus yang diusulkan tim. Satuannya berbobot ETA,
  sehingga tidak boleh dicampurkan dengan objective wajib dalam perbandingan.

Patch awal tidak diterapkan utuh: kelas `Kapal`, `Kendaraan`, `Penempatan`,
`Keadaan` dibuang; `tarif`/`eta` menjadi `tarif_kirim`/`eta_hari`; titik asal
kiri bawah dan makna orientasi patch diganti sesuai kontrak. Struktur repo
dipertahankan, hanya utilitas dan tes ditambahkan. Tidak ada algoritma,
fungsi tetangga, ataupun optimasi dalam perubahan ini.
