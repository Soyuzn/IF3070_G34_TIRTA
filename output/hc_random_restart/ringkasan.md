# Eksperimen hill_climbing

Objektif: jumlah tarif_kirim (juta rupiah).
Hasil pencarian nyata pada dataset sintetis, bukan bukti optimum global.

| Ulangan | Seed | OF awal | OF akhir | Iterasi | Durasi (s) | Stuck |
|---|---|---|---|---|---|---|
| 1 | 40 | 404.000 | 429.000 | 54 | 0.816994 | - |
| 2 | 41 | 412.000 | 423.000 | 46 | 0.777754 | - |
| 3 | 42 | 414.000 | 426.000 | 54 | 0.891504 | - |

Rata-rata OF akhir: 426.000; simpangan baku sampel: 3.000.
Rata-rata durasi pencarian: 0.828751 detik.
Stuck mengikuti pemeriksa yang diberikan; tanda - berarti belum diukur.
Parameter, snapshot data, kedua state, dan metrik ada di hasil.json tiap ulangan.
