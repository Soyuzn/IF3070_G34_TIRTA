# Kontrak data

`data/kendaraan.json` berisi `id`, `lebar`, `panjang`, `berat`, `tarif_kirim`, dan `eta_hari`.
`data/kapal.json` berisi list satu kapal: `id`, `lebar`, `panjang`, `kapasitas`.
`kapal_bonus.json` cuma data lama, tidak dipakai program.

Ukuran dan koordinat pakai sel grid. Berat dan kapasitas pakai unit yang sama,
bukan jumlah kendaraan. Tarif dalam juta rupiah, ETA dalam sisa hari.
Angka dataset sintetis. ETA belum dipakai untuk menghitung objektif.

## State

Setiap ID kendaraan harus ada. Nilainya penempatan atau `None` kalau di luar kapal
(`null` di JSON). Contoh potongannya:

```json
{
  "lcgc_01": {"kapal_id": "kapal_utama", "x": 0, "y": 0, "orientasi": "vertikal"},
  "lcgc_02": null
}
```

State lengkap tetap berisi semua 30 kendaraan. `kapal_id` harus cocok dengan data kapal.
Koordinat `(x, y)` menunjuk sudut kiri atas kendaraan. Titik `(0, 0)` ada di kiri atas dek,
`x` ke kanan dan `y` ke bawah. Vertikal memakai lebar di sumbu x dan panjang di sumbu y.
Horizontal menukar keduanya.

State dicek lewat `periksa_state()` di `src/data.py`: semua ID lengkap, penempatan di dalam
batas dek, tidak bertumpuk, dan total berat tidak melebihi kapasitas.
`nilai_objektif()` menjumlahkan tarif kendaraan yang dimuat setelah validasi.
Kendaraan di luar kapal tidak menambah nilai.

## Dipakai semua algoritma

Masukan berupa list `kapal`, list `kendaraan`, dan dict `state_awal`.
Masing-masing modul punya fungsi `cari(kapal, kendaraan, state_awal, seed, **parameter)`.
Hasilnya `(state_akhir, riwayat, metrik)`:

- `state_akhir`: susunan terbaik yang ditemukan, harus valid.
- `riwayat`: list dict, mulai iterasi 0. HC/SA mengisi `objektif`, GA mengisi
  `maksimum_populasi` dan `rata_rata_populasi`. Satu iterasi GA berarti satu generasi.
- `metrik`: dict tambahan, misalnya populasi awal/akhir GA, stuck SA, atau restart HC.

Pakai `random.Random(seed)` dan salin state sebelum mengubahnya.
Data dan state awal milik pemanggil tidak ikut diubah.

HC stochastic dan SA mengambil kandidat lewat `tetangga_acak()` di `src/tetangga.py`.
Hasilnya `(state_baru, langkah)` atau `None` kalau sampling gagal.
Steepest dan sideways memakai `semua_tetangga()`.

## Hasil run

Durasi hanya mengukur pencarian. Pembentukan populasi GA ikut dihitung;
baca data, state acak pertama, simpan hasil, dan gambar berada di luar timer.
State awal yang dicatat untuk GA adalah individu terbaik populasi awal.

Grafik SA menunjukkan state saat ini, jadi nilainya bisa berbeda dari state terbaik.
Pada random restart, indeks iterasi terus naik. Baris state awal restart ikut masuk
riwayat, tetapi tidak masuk hitungan langkah pada `iterasi_per_restart`.
