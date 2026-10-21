import copy
import random
import tempfile
import unittest
from pathlib import Path

from src.data import (baca_data, baca_json, inisialisasi_acak, nilai_objektif,
                      periksa_data, periksa_state, ukuran)

ROOT = Path(__file__).resolve().parents[1]


class UjiData(unittest.TestCase):
    def setUp(self):
        self.kapal = [dict(id="k", lebar=3, panjang=5, kapasitas=4)]
        self.kendaraan = [dict(id="a", lebar=2, panjang=3, tarif_kirim=20, berat=3, eta_hari=0),
                          dict(id="b", lebar=1, panjang=1, tarif_kirim=7, berat=2, eta_hari=5)]
        self.p = dict(kapal_id="k", x=0, y=0, orientasi="vertikal")

    def test_orientasi_batas_dan_objektif(self):
        self.assertEqual(ukuran(self.kendaraan[0], "vertikal"), (2, 3))
        self.assertEqual(ukuran(self.kendaraan[0], "horizontal"), (3, 2))
        for orientasi, x, y in (("vertikal", 1, 2), ("horizontal", 0, 3)):
            state = dict(a=dict(self.p, x=x, y=y, orientasi=orientasi), b=None)
            self.assertEqual(nilai_objektif(self.kapal, self.kendaraan, state), 20)
        self.assertEqual(nilai_objektif(self.kapal, self.kendaraan, dict(a=None, b=None)), 0)

    def test_state_tidak_valid_ditolak(self):
        kasus = [dict(a=self.p), dict(a=None, b=None, c=None)]
        for perubahan in (dict(x=-1), dict(x=2), dict(y=3), dict(x=.5), dict(y=True),
                          dict(x=None), dict(orientasi="Vertical"), dict(kapal_id="asing"),
                          dict(ekstra=1)):
            kasus.append(dict(a=dict(self.p, **perubahan), b=None))
        for state in kasus:
            with self.subTest(state=state), self.assertRaises(ValueError):
                periksa_state(self.kapal, self.kendaraan, state)

    def test_tumpang_tindih_dan_kapasitas_terpisah(self):
        for x, y in ((0, 0), (2, 4)):
            state = dict(a=self.p, b=dict(self.p, x=x, y=y))
            with self.subTest(x=x, y=y), self.assertRaises(ValueError):
                periksa_state(self.kapal, self.kendaraan, state)
        kapal = [dict(self.kapal[0], kapasitas=5)]
        periksa_state(kapal, self.kendaraan, dict(a=self.p, b=dict(self.p, x=2, y=4)))

    def test_skenario_harus_tepat_satu_kapal(self):
        kapal = self.kapal + [dict(self.kapal[0], id="k2")]
        with self.assertRaisesRegex(ValueError, "tepat satu kapal"):
            periksa_data(kapal, self.kendaraan)
        with self.assertRaisesRegex(ValueError, "tepat satu kapal"):
            inisialisasi_acak(kapal, self.kendaraan, 42)

    def test_hanya_tarif_kirim_dan_eta_tidak_memengaruhi_nilai(self):
        kapal = [dict(self.kapal[0], kapasitas=5)]
        state = dict(a=self.p, b=dict(self.p, x=2, y=4))
        self.assertEqual(nilai_objektif(kapal, self.kendaraan, state), 27)
        kendaraan = [dict(k, eta_hari=100) for k in self.kendaraan]
        self.assertEqual(nilai_objektif(kapal, kendaraan, state), 27)
        for objektif in ("tarif_eta", "asing"):
            with self.subTest(objektif=objektif), self.assertRaises(ValueError):
                nilai_objektif(kapal, kendaraan, state, objektif)

    def test_data_rusak_ditolak(self):
        for kolom, nilai in (("lebar", True), ("panjang", 0), ("berat", -1),
                              ("tarif_kirim", float("nan")), ("berat", float("inf")),
                              ("eta_hari", -.5), ("id", "")):
            kendaraan = copy.deepcopy(self.kendaraan)
            kendaraan[0][kolom] = nilai
            with self.subTest(kolom=kolom), self.assertRaises(ValueError):
                periksa_data(self.kapal, kendaraan)
        with self.assertRaises(ValueError):
            periksa_data(self.kapal, self.kendaraan * 2)
        with self.assertRaises(ValueError):
            periksa_data(self.kapal * 2, self.kendaraan)

    def test_json_tidak_menyembunyikan_id_berulang(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"
            path.write_text('{"a": null, "a": null}', encoding="utf-8")
            with self.assertRaises(ValueError):
                baca_json(path)

    def test_berat_dan_kapasitas_boleh_pecahan_positif(self):
        kapal = [dict(self.kapal[0], kapasitas=.75)]
        kendaraan = [dict(self.kendaraan[0], berat=.5)]
        periksa_state(kapal, kendaraan, {"a": self.p})
        for kolom in ("berat", "kapasitas"):
            for nilai in (0, -1, True, float("nan"), float("inf")):
                data_kapal, data_kendaraan = copy.deepcopy((kapal, kendaraan))
                daftar = data_kapal if kolom == "kapasitas" else data_kendaraan
                daftar[0][kolom] = nilai
                with self.subTest(kolom=kolom, nilai=nilai), self.assertRaises(ValueError):
                    periksa_data(data_kapal, data_kendaraan)

    def test_seed_dataset_asli_tanpa_mutasi_atau_rng_global(self):
        kapal, kendaraan = baca_data(ROOT / "data/kapal.json", ROOT / "data/kendaraan.json")
        sebelum = copy.deepcopy((kapal, kendaraan))
        rng = random.getstate()
        hasil = []
        for seed in range(10):
            state = inisialisasi_acak(kapal, kendaraan, seed)
            periksa_state(kapal, kendaraan, state)
            self.assertEqual(state, inisialisasi_acak(kapal, kendaraan, seed))
            hasil.append(state)
        self.assertTrue(any(state != hasil[0] for state in hasil[1:]))
        self.assertEqual((kapal, kendaraan), sebelum)
        self.assertEqual(random.getstate(), rng)

    def test_kendaraan_tidak_muat_tetap_null(self):
        kendaraan = [dict(self.kendaraan[0], lebar=99), dict(self.kendaraan[1], berat=99)]
        self.assertEqual(inisialisasi_acak(self.kapal, kendaraan, 1), dict(a=None, b=None))
        with self.assertRaises(ValueError):
            inisialisasi_acak(self.kapal, kendaraan, None)


if __name__ == "__main__":
    unittest.main()
