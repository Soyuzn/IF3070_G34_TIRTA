# Analisis eksperimen TIRTA

Status: belum dijalankan. Isi dengan hasil nyata; jangan pakai keluaran ilustrasi.

## Kondisi pengujian

- Commit, dataset, kapal, kapasitas, perangkat, versi Python:
- Objective: jumlah `tarif_kirim` (juta rupiah), atau bonus yang dilaporkan terpisah:
- Definisi iterasi, kriteria berhenti, varian HC, definisi/satuan stuck SA:
- Daftar seed inisialisasi dan pencarian, seluruh parameter tiap konfigurasi:
- Durasi: proses pencarian saja, tanpa inisialisasi, plotting, dan penyimpanan:
- GA: state representatif adalah individu terbaik; sertakan populasi awal/akhir:

## Rencana percobaan

| Kelompok | Kontrol | Variasi | Ulangan |
|---|---|---|---|
| HC | Dataset dan parameter HC | Seed | 3 |
| SA | Dataset dan parameter SA | Seed | 3 |
| GA A | Dataset dan jumlah populasi | 3 batas iterasi | 3 per konfigurasi |
| GA B | Dataset dan batas iterasi | 3 jumlah populasi | 3 per konfigurasi |

## Hasil per percobaan

| Algoritma / konfigurasi | Ulangan | Seed | Objektif awal | Objektif akhir | Iterasi | Durasi (detik) | Direktori hasil |
|---|---|---|---|---|---|---|---|

Lampirkan gambar state awal/akhir, kurva objective, kurva exp(ΔE/T) SA,
serta kurva maksimum dan rata-rata populasi GA. Catat jumlah restart dan
iterasi per restart bila berlaku; sertakan `frekuensi_stuck` beserta satuannya.

## Ringkasan per konfigurasi

| Konfigurasi | n | Rata-rata objektif akhir | Simpangan baku sampel | Min | Maks | Rata-rata durasi (detik) |
|---|---|---|---|---|---|---|---|

## Pembahasan

1. Bandingkan objective, durasi, dan konsistensi ketiga algoritma pada dataset sama.
2. Hubungkan pola kurva dengan kriteria berhenti; jelaskan kendaraan yang dimuat
   atau tersisa di luar dan pemakaian kapasitas pada solusi akhir.
3. SA: jelaskan eksponen penerimaan, penurunan objective, dan frekuensi stuck.
4. GA: bahas pengaruh batas iterasi dan jumlah populasi pada kedua kelompok uji.
5. Jika optimum global belum terbukti, sebut hasil terbaik teramati; jangan
   menyebutnya optimum. Jika memakai batas atas, jelaskan asal dan keterbatasannya.
6. Tuliskan kesimpulan, keterbatasan, dan saran yang didukung percobaan.

Laporan PDF akhir tetap memuat pembahasan implementasi anggota lain,
pembagian tugas, referensi, dan lampiran penggunaan Generative AI.
