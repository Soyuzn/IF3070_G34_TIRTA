# Eksperimen simulated_annealing

Objektif: jumlah tarif_kirim (juta rupiah).
Hasil pencarian nyata pada dataset sintetis, bukan bukti optimum global.

| Ulangan | Seed | OF awal | OF akhir | Iterasi | Durasi (s) | Stuck |
|---|---|---|---|---|---|---|
| 1 | 40 | 404.000 | 413.000 | 1000 | 0.555946 | 0.000 |
| 2 | 41 | 412.000 | 420.000 | 1000 | 0.565304 | 0.000 |
| 3 | 42 | 414.000 | 417.000 | 1000 | 0.517211 | 0.050 |

Rata-rata OF akhir: 416.667; simpangan baku sampel: 3.512.
Rata-rata durasi pencarian: 0.546154 detik.
Stuck mengikuti pemeriksa yang diberikan; tanda - berarti belum diukur.
Parameter, snapshot data, kedua state, dan metrik ada di hasil.json tiap ulangan.
