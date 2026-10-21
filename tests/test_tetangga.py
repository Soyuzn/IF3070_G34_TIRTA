import copy
import random
import unittest
from pathlib import Path

from src.data import baca_data, inisialisasi_acak, periksa_state
from src.tetangga import tetangga_acak

ROOT = Path(__file__).resolve().parents[1]


class UjiTetangga(unittest.TestCase):
    def test_tetangga_acak_valid_dan_state_asli_utuh(self):
        for nama_kapal in ("kapal.json", "kapal_bonus.json"):
            kapal, kendaraan = baca_data(ROOT / "data" / nama_kapal, ROOT / "data/kendaraan.json")
            for seed in range(50):
                with self.subTest(kapal=nama_kapal, seed=seed):
                    state = inisialisasi_acak(kapal, kendaraan, seed)
                    salinan = copy.deepcopy(state)
                    baru, move = tetangga_acak(kapal, kendaraan, state, random.Random(seed))
                    self.assertEqual(state, salinan)
                    self.assertNotEqual(baru, state)
                    self.assertIn(move[0], ("pindah", "putar", "tukar"))
                    periksa_state(kapal, kendaraan, baru)


if __name__ == "__main__":
    unittest.main()