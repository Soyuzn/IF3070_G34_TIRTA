import copy
import json
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.data import baca_data, baca_json, inisialisasi_acak, nilai_objektif, periksa_state
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

    def test_hanya_perbaikan_diterima_dan_batas_gagal_diulang_setelah_naik(self):
        kapal = [dict(id="k", lebar=1, panjang=1, kapasitas=1)]
        kendaraan = [dict(id="a", lebar=1, panjang=1, berat=1, tarif_kirim=10, eta_hari=0)]
        awal = dict(a=None)
        penuh = dict(a=dict(kapal_id="k", x=0, y=0, orientasi="vertikal"))
        kandidat = [(awal, ("uji",)), (penuh, ("uji",)),
                    (awal, ("uji",)), (penuh, ("uji",))]
        rng = random.getstate()
        with patch("src.hill_climbing.tetangga_acak", side_effect=kandidat) as tetangga:
            akhir, riwayat, _ = cari(kapal, kendaraan, awal, 1, maks_gagal=2)
        self.assertEqual(tetangga.call_count, 4)
        self.assertEqual([b["objektif"] for b in riwayat], [0, 0, 10, 10, 10])
        self.assertEqual(akhir, penuh)
        self.assertEqual(awal, dict(a=None))
        self.assertEqual(random.getstate(), rng)

    def test_nol_langkah_tidak_membagi_state_dan_parameter_salah_ditolak(self):
        kapal, kendaraan = baca_data()
        awal = inisialisasi_acak(kapal, kendaraan, 7)
        with patch("src.hill_climbing.tetangga_acak") as tetangga:
            akhir, riwayat, _ = cari(kapal, kendaraan, awal, 7, maks_gagal=0)
            tetangga.assert_not_called()
        self.assertEqual(akhir, awal)
        self.assertIsNot(akhir, awal)
        self.assertEqual(len(riwayat), 1)
        for id, posisi in akhir.items():
            if posisi is not None:
                self.assertIsNot(posisi, awal[id])
        for parameter in (dict(seed=True), dict(maks_gagal=-1),
                          dict(maks_gagal=True), dict(maks_gagal=1.5),
                          dict(maks_sideways=-1), dict(maks_sideways=True),
                          dict(maks_restart=-1), dict(maks_restart=1.5)):
            with self.subTest(parameter=parameter), self.assertRaises(ValueError):
                cari(kapal, kendaraan, awal, **(dict(seed=7) | parameter))

    def test_runner_menyimpan_hasil_stochastic_dan_gambar(self):
        with tempfile.TemporaryDirectory() as tmp:
            tujuan = Path(tmp) / "hc"
            proses = subprocess.run(
                [sys.executable, "-m", "src.eksperimen", "--modul", "src.hill_climbing",
                 "--output", str(tujuan), "--parameter", json.dumps(dict(maks_gagal=5))],
                cwd=ROOT, capture_output=True, text=True, timeout=60)
            self.assertEqual(proses.returncode, 0, proses.stderr)
            for seed in (40, 41, 42):
                folder = tujuan / f"ulangan_{seed - 39}_seed_{seed}"
                hasil = baca_json(folder / "hasil.json")
                self.assertEqual(hasil["metrik"]["varian"], "stochastic")
                self.assertEqual(hasil["parameter"]["maks_gagal"], 5)
                self.assertEqual(hasil["objektif"], "jumlah tarif_kirim")
                self.assertGreaterEqual(hasil["objektif_akhir"], hasil["objektif_awal"])
                self.assertEqual(len(list(folder.glob("*.png"))), 3)

    def test_semua_varian_valid_dan_tidak_turun_dari_awal(self):
        kapal, kendaraan = baca_data(ROOT / "data/kapal.json", ROOT / "data/kendaraan.json")
        awal = inisialisasi_acak(kapal, kendaraan, 3)
        sebelum = copy.deepcopy((kapal, kendaraan, awal))
        rng = random.getstate()
        nilai_awal = nilai_objektif(kapal, kendaraan, awal)
        for varian in VARIAN:
            with self.subTest(varian=varian):
                parameter = dict(varian=varian, maks_gagal=100, maks_sideways=5, maks_restart=2)
                hasil = cari(kapal, kendaraan, awal, 3, **parameter)
                self.assertEqual(hasil, cari(kapal, kendaraan, awal, 3, **parameter))
                akhir, riwayat, metrik = hasil
                periksa_riwayat(riwayat)
                self.assertGreaterEqual(nilai_objektif(kapal, kendaraan, akhir), nilai_awal)
                self.assertEqual((kapal, kendaraan, awal), sebelum)
                self.assertEqual(random.getstate(), rng)
                if varian == "sideways":
                    self.assertLessEqual(metrik["jumlah_sideways"], 5)
                if varian == "random_restart":
                    self.assertEqual(len(metrik["iterasi_per_restart"]), 3)
        with self.assertRaises(ValueError):
            cari(kapal, kendaraan, awal, 3, varian="asing")

    def test_sideways_berhenti_tepat_saat_batas_tercapai(self):
        kapal = [dict(id="k", lebar=1, panjang=1, kapasitas=1)]
        kendaraan = [dict(id="a", lebar=1, panjang=1, berat=1, tarif_kirim=10, eta_hari=0)]
        awal = dict(a=dict(kapal_id="k", x=0, y=0, orientasi="vertikal"))
        putar = dict(a=dict(awal["a"], orientasi="horizontal"))
        with patch("src.hill_climbing.semua_tetangga",
                   return_value=[(putar, ("putar", "a"))]) as tetangga:
            akhir, riwayat, metrik = cari(kapal, kendaraan, awal, 1,
                                          varian="sideways", maks_sideways=1)
        tetangga.assert_called_once()
        self.assertEqual(akhir, putar)
        self.assertEqual([b["objektif"] for b in riwayat], [10, 10])
        self.assertEqual(metrik["jumlah_sideways"], 1)

    def test_restart_mencatat_semua_run_dan_mengembalikan_terbaik(self):
        kapal = [dict(id="k", lebar=2, panjang=1, kapasitas=1)]
        kendaraan = [dict(id="a", lebar=1, panjang=1, berat=1, tarif_kirim=10, eta_hari=0),
                     dict(id="b", lebar=1, panjang=2, berat=1, tarif_kirim=20, eta_hari=0)]
        awal = dict(a=None, b=None)
        buntu = dict(a=dict(kapal_id="k", x=1, y=0, orientasi="vertikal"), b=None)
        with patch("src.hill_climbing.inisialisasi_acak", side_effect=[awal, buntu]):
            akhir, riwayat, metrik = cari(kapal, kendaraan, awal, 1,
                                          varian="random_restart", maks_restart=2)
        periksa_riwayat(riwayat)
        self.assertEqual(nilai_objektif(kapal, kendaraan, akhir), 20)
        self.assertEqual(riwayat[-1]["objektif"], 10)
        self.assertEqual(metrik["jumlah_restart"], 2)
        self.assertEqual(metrik["iterasi_per_restart"], [1, 1, 0])
        self.assertEqual([b["restart"] for b in riwayat], [0, 0, 1, 1, 2])


if __name__ == "__main__":
    unittest.main()
