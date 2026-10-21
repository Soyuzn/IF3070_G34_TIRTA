import copy
import unittest
from pathlib import Path

from src.data import baca_data, inisialisasi_acak, nilai_objektif, periksa_state
from src.hill_climbing import cari

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


if __name__ == "__main__":
    unittest.main()
