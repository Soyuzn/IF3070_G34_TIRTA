# Kontrak data dan state

Data kendaraan ada di `data/kendaraan.json`: `id`, `lebar`, `panjang`,
`tarif_kirim`, `berat`, `eta_hari`. Data kapal ada di `data/kapal.json`:
`id`, `lebar`, `panjang`, `kapasitas`. Untuk bonus multi-kapal, pakai
`data/kapal_bonus.json` dengan daftar kendaraan yang sama. Angkanya sintetis.

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
`berat` tiap kapal tidak melebihi `kapasitas`. Nilai state valid adalah jumlah
`tarif_kirim` kendaraan yang dimuat. Kendaraan di luar kapal bernilai nol.

Satuan: ukuran dan koordinat dalam sel grid, tarif kirim dalam juta rupiah,
berat dan kapasitas dalam unit yang sama, ETA dalam sisa hari. `eta_hari`
tidak menjadi batasan pada objective wajib. `kapal_id` tetap ada meskipun
skenario wajib hanya memakai satu kapal.

Untuk bonus objective `tarif_eta`, nilainya adalah jumlah
`tarif_kirim / (1 + eta_hari)` dari kendaraan yang dimuat. Kendaraan yang
lebih cepat tiba mendapat bobot lebih besar. Ini pilihan tim, bukan aturan
wajib soal; jangan campur angka objective bonus dengan objective wajib dalam
satu perbandingan.

Kode bersama dan format keluaran algoritma dijelaskan di [integrasi](integrasi.md).
