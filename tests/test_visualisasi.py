import importlib.util
import unittest
from pathlib import Path

from src.data import baca_data, inisialisasi_acak


@unittest.skipUnless(importlib.util.find_spec("matplotlib"), "Matplotlib belum tersedia")
class UjiVisualisasi(unittest.TestCase):
    def test_grafik_mengikuti_sumbu_kontrak_dan_tidak_mengubah_state(self):
        import copy
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from src.visualisasi import gambar_state, gambar_riwayat, gambar_penerimaan
        root = Path(__file__).resolve().parents[1]
        kapal, kendaraan = baca_data(root / "data/kapal.json", root / "data/kendaraan.json")
        state = inisialisasi_acak(kapal, kendaraan, 42)
        sebelum = copy.deepcopy(state)
        fig = gambar_state(kapal, kendaraan, state)
        self.assertEqual(len(fig.axes), 1)
        self.assertEqual(len(fig.axes[0].patches), sum(p is not None for p in state.values()))
        self.assertEqual(fig.axes[0].get_ylim(), (kapal[0]["panjang"], 0))
        fig.canvas.draw()
        plt.close(fig)
        self.assertEqual(state, sebelum)
        riwayat = [dict(iterasi=0, objektif=10),
                   dict(iterasi=1, objektif=8, eksponen_penerimaan=.5)]
        for fungsi in (gambar_riwayat, gambar_penerimaan):
            fig = fungsi(riwayat)
            self.assertEqual(len(fig.axes[0].lines), 1)
            fig.canvas.draw()
            plt.close(fig)

    def test_grafik_maksimum_dan_rata_rata_ga(self):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from src.visualisasi import gambar_riwayat

        riwayat_ga = [dict(iterasi=0, maksimum_populasi=10, rata_rata_populasi=5),
                      dict(iterasi=1, maksimum_populasi=12, rata_rata_populasi=6)]
        fig = gambar_riwayat(riwayat_ga)
        self.assertEqual(fig.axes[0].get_ylabel(), "Objektif (juta rupiah)")
        garis = fig.axes[0].lines
        self.assertEqual([g.get_label() for g in garis],
                         ["Maksimum populasi", "Rata-rata populasi"])
        self.assertEqual([list(g.get_ydata()) for g in garis], [[10, 12], [5, 6]])
        plt.close(fig)


if __name__ == "__main__":
    unittest.main()
