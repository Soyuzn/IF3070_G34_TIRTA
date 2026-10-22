# Eksperimen hill_climbing

Objektif: jumlah tarif_kirim (juta rupiah).
Hasil pencarian nyata pada dataset sintetis, bukan bukti optimum global.

| Ulangan | Seed | OF awal | OF akhir | Iterasi | Durasi (s) | Stuck |
|---|---|---|---|---|---|---|
| 1 | 40 | 404.000 | 409.000 | 103 | 1.323967 | - |
| 2 | 41 | 412.000 | 424.000 | 104 | 1.682145 | - |
| 3 | 42 | 414.000 | 425.000 | 103 | 1.776858 | - |

Rata-rata OF akhir: 419.333; simpangan baku sampel: 8.963.
Rata-rata durasi pencarian: 1.594323 detik.
Stuck mengikuti pemeriksa yang diberikan; tanda - berarti belum diukur.
Parameter, snapshot data, kedua state, dan metrik ada di hasil.json tiap ulangan.
