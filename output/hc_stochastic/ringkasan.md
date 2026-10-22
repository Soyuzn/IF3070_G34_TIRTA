# Eksperimen hill_climbing

Objektif: jumlah tarif_kirim (juta rupiah).
Hasil pencarian nyata pada dataset sintetis, bukan bukti optimum global.

| Ulangan | Seed | OF awal | OF akhir | Iterasi | Durasi (s) | Stuck |
|---|---|---|---|---|---|---|
| 1 | 40 | 404.000 | 410.000 | 1125 | 0.558499 | - |
| 2 | 41 | 412.000 | 421.000 | 2259 | 1.277588 | - |
| 3 | 42 | 414.000 | 425.000 | 1635 | 0.811369 | - |

Rata-rata OF akhir: 418.667; simpangan baku sampel: 7.767.
Rata-rata durasi pencarian: 0.882485 detik.
Stuck mengikuti pemeriksa yang diberikan; tanda - berarti belum diukur.
Parameter, snapshot data, kedua state, dan metrik ada di hasil.json tiap ulangan.
