import copy
import unittest
from pathlib import Path

from src.data import baca_data, inisialisasi_acak, nilai_objektif, periksa_state
from src.hill_climbing import VARIAN, cari
from src.pencatatan import periksa_riwayat

ROOT = Path(__file__).resolve().parents[1]


class UjiHillClimbing(unittest.TestCase):
    def test_stochastic_naik_valid_dan_bisa_diulang(self):
        kapal, kendaraan = baca_data(ROOT / "data/kapal.json", ROOT / "data/kendaraan.json")
        awal = inisialisasi_acak(kapal, kendaraan, 7)
        salinan = copy.deepcopy(awal)
        akhir, riwayat, _ = cari(kapal, kendaraan, awal, seed=7, maks_gagal=200)
        self.assertEqual(awal, salinan)
        periksa_state(kapal, kendaraan, akhir)
        nilai = [b["objektif"] for b in riwayat]
        self.assertEqual(nilai, sorted(nilai))
        self.assertEqual(nilai[-1], nilai_objektif(kapal, kendaraan, akhir))
        self.assertEqual(cari(kapal, kendaraan, awal, seed=7, maks_gagal=200)[0], akhir)

    def test_semua_varian_valid_dan_tidak_turun_dari_awal(self):
        kapal, kendaraan = baca_data(ROOT / "data/kapal.json", ROOT / "data/kendaraan.json")
        awal = inisialisasi_acak(kapal, kendaraan, 3)
        nilai_awal = nilai_objektif(kapal, kendaraan, awal)
        for varian in VARIAN:
            with self.subTest(varian=varian):
                akhir, riwayat, metrik = cari(kapal, kendaraan, awal, 3, varian=varian,
                                              maks_gagal=100, maks_sideways=5, maks_restart=2)
                periksa_riwayat(riwayat)
                self.assertGreaterEqual(nilai_objektif(kapal, kendaraan, akhir), nilai_awal)
                if varian == "sideways":
                    self.assertLessEqual(metrik["jumlah_sideways"], 5)
                if varian == "random_restart":
                    self.assertEqual(len(metrik["iterasi_per_restart"]), 3)
        with self.assertRaises(ValueError):
            cari(kapal, kendaraan, awal, 3, varian="asing")


if __name__ == "__main__":
    unittest.main()
