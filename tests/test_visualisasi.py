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
        ax = fig.axes[0]
        self.assertEqual(len(ax.patches), sum(p is not None for p in state.values()))
        self.assertEqual(ax.get_ylim(), (kapal[0]["panjang"], 0))
        self.assertEqual(list(ax.get_xticks()), list(range(kapal[0]["lebar"] + 1)))
        self.assertEqual(list(ax.get_yticks()), list(range(kapal[0]["panjang"] + 1)))
        luar = next(t.get_text() for t in fig.texts if t.get_text().startswith("Di luar kapal:"))
        self.assertEqual(" ".join(luar.split()), "Di luar kapal: " + ", ".join(
            k["id"] for k in kendaraan if state[k["id"]] is None))
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

    def test_objektif_bonus_ditolak(self):
        import matplotlib
        matplotlib.use("Agg")
        from src.visualisasi import gambar_state, gambar_riwayat

        root = Path(__file__).resolve().parents[1]
        kapal, kendaraan = baca_data(root / "data/kapal.json", root / "data/kendaraan.json")
        state = inisialisasi_acak(kapal, kendaraan, 42)
        with self.assertRaisesRegex(ValueError, "hanya tarif_kirim"):
            gambar_state(kapal, kendaraan, state, objektif="tarif_eta")
        with self.assertRaisesRegex(ValueError, "hanya tarif_kirim"):
            gambar_riwayat([dict(iterasi=0, objektif=0)], objektif="tarif_eta")


if __name__ == "__main__":
    unittest.main()
