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
        for nama in ("kapal.json", "kapal_bonus.json"):
            kapal, kendaraan = baca_data(root / "data" / nama, root / "data/kendaraan.json")
            state = inisialisasi_acak(kapal, kendaraan, 42)
            sebelum = copy.deepcopy(state)
            fig = gambar_state(kapal, kendaraan, state)
            self.assertEqual(len(fig.axes), len(kapal))
            self.assertEqual(sum(len(ax.patches) for ax in fig.axes),
                             sum(p is not None for p in state.values()))
            for ax, dek in zip(fig.axes, kapal):
                self.assertEqual(ax.get_ylim(), (dek["panjang"], 0))
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


if __name__ == "__main__":
    unittest.main()
