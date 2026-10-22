# Eksperimen hill_climbing

Objektif: jumlah tarif_kirim (juta rupiah).
Hasil pencarian nyata pada dataset sintetis, bukan bukti optimum global.

| Ulangan | Seed | OF awal | OF akhir | Iterasi | Durasi (s) | Stuck |
|---|---|---|---|---|---|---|
| 1 | 40 | 404.000 | 409.000 | 3 | 0.051673 | - |
| 2 | 41 | 412.000 | 421.000 | 3 | 0.082582 | - |
| 3 | 42 | 414.000 | 425.000 | 3 | 0.079347 | - |

Rata-rata OF akhir: 418.333; simpangan baku sampel: 8.327.
Rata-rata durasi pencarian: 0.071201 detik.
Stuck mengikuti pemeriksa yang diberikan; tanda - berarti belum diukur.
Parameter, snapshot data, kedua state, dan metrik ada di hasil.json tiap ulangan.
