# Kontrak data dan state

Data kendaraan ada di `data/kendaraan.json`: `id`, `lebar`, `panjang`,
`tarif_kirim`, `berat`, `eta_hari`. Data kapal ada di `data/kapal.json`:
`id`, `lebar`, `panjang`, `kapasitas`. Program memakai tepat satu kapal dalam list.
`data/kapal_bonus.json` disimpan sebagai data lama dan tidak dipakai. Angkanya sintetis.

Satu state adalah peta dari **setiap ID kendaraan** ke penempatannya.
Kendaraan di luar kapal bernilai `null`. Kendaraan yang dimuat ditulis seperti ini:

```json
{
  "lcgc_01": {"kapal_id": "kapal_utama", "x": 0, "y": 0, "orientasi": "vertikal"},
  "lcgc_02": null
}
```

Contoh di atas hanya menunjukkan bentuknya. State asli harus memuat semua
kendaraan. `(x, y)` adalah sel kiri atas kendaraan; `(0, 0)` ada di kiri atas
dek. Sumbu `x` ke kanan, `y` ke bawah. Orientasi `vertikal` memakai `lebar`
di sumbu `x` dan `panjang` di sumbu `y`. Orientasi `horizontal` menukarnya.

State valid jika setiap kendaraan muncul sekali, seluruh bagian kendaraan
yang dimuat berada dalam dek, tidak ada sel yang bertabrakan, dan total
`berat` muatan tidak melebihi `kapasitas` kapal. Nilai state valid adalah jumlah
`tarif_kirim` kendaraan yang dimuat. Kendaraan di luar kapal bernilai nol.

Satuan: ukuran dan koordinat dalam sel grid, tarif kirim dalam juta rupiah,
berat dan kapasitas dalam unit yang sama, ETA dalam sisa hari. `eta_hari`
tidak dipakai dalam perhitungan fitness. `kapal_id` tetap mengikuti kontrak
state dan harus cocok dengan ID kapal yang digunakan.

Kode bersama dan format keluaran algoritma dijelaskan di [integrasi](integrasi.md).
