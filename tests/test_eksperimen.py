import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.data import baca_data, baca_json, inisialisasi_acak, nilai_objektif
from src.eksperimen import jalankan
from src.pencatatan import simpan_percobaan
from src.simulated_annealing import cari as cari_sa

ROOT = Path(__file__).resolve().parents[1]


class UjiEksperimen(unittest.TestCase):
    def test_timer_hanya_membungkus_pencarian_dan_semua_seed_tersimpan(self):
        kapal, kendaraan = baca_data()
        kejadian = []

        def awal(*args):
            kejadian.append("inisialisasi")
            return inisialisasi_acak(*args)

        def cari(kapal, kendaraan, state, seed, **parameter):
            kejadian.append("cari")
            nilai = nilai_objektif(kapal, kendaraan, state)
            return state, [dict(iterasi=0, objektif=nilai)], {}

        def jam():
            kejadian.append("jam")
            return float(len(kejadian))

        def simpan(*args, **kwargs):
            kejadian.append("simpan")
            return simpan_percobaan(*args, **kwargs)

        with tempfile.TemporaryDirectory() as tmp:
            tujuan = Path(tmp) / "uji"
            with patch("src.eksperimen.inisialisasi_acak", side_effect=awal), \
                    patch("src.pencatatan.perf_counter", side_effect=jam), \
                    patch("src.eksperimen.simpan_percobaan", side_effect=simpan):
                hasil = jalankan(cari, kapal, kendaraan, tujuan, grafik=False)
            self.assertEqual(kejadian, ["inisialisasi", "jam", "cari", "jam", "simpan"] * 3)
            self.assertEqual([h["seed"] for h in hasil], [40, 41, 42])
            for h in hasil:
                data = baca_json(tujuan / h["direktori"] / "hasil.json")
                self.assertEqual(data["objektif"], "jumlah tarif_kirim")
                self.assertEqual(data["durasi_detik"], 2)
            with (tujuan / "ringkasan.csv").open(newline="") as berkas:
                self.assertEqual(len(list(csv.DictReader(berkas))), 3)
            self.assertTrue((tujuan / "ringkasan.md").exists())
            with self.assertRaises(FileExistsError):
                jalankan(cari, kapal, kendaraan, tujuan, grafik=False)

    def test_runner_ga_mencatat_terbaik_populasi_awal_dan_parameter_efektif(self):
        kapal, kendaraan = baca_data()
        with tempfile.TemporaryDirectory() as tmp:
            tujuan = Path(tmp) / "ga"
            proses = subprocess.run(
                [sys.executable, "-m", "src.eksperimen", "--modul", "src.genetic",
                 "--output", str(tujuan), "--seed", "1", "--tanpa-grafik",
                 "--parameter", json.dumps(dict(batas_iterasi=2))],
                cwd=ROOT, capture_output=True, text=True, timeout=60)
            self.assertEqual(proses.returncode, 0, proses.stderr)
            data = baca_json(tujuan / "ulangan_1_seed_1/hasil.json")
            populasi = data["metrik"]["populasi_awal"]
            terbaik = max(populasi, key=lambda p: nilai_objektif(kapal, kendaraan, p))
            self.assertEqual(data["state_awal"], terbaik)
            self.assertEqual(data["objektif_awal"], data["riwayat"][0]["maksimum_populasi"])
            self.assertGreater(data["objektif_awal"],
                               nilai_objektif(kapal, kendaraan, populasi[0]))
            self.assertEqual(data["parameter"], dict(jumlah_populasi=20, batas_iterasi=2,
                                                    peluang_mutasi=.2))
            with (tujuan / "ringkasan.csv").open(newline="") as berkas:
                ringkasan = next(csv.DictReader(berkas))
            self.assertEqual(float(ringkasan["objektif_awal"]), data["objektif_awal"])

    def test_seed_duplikat_dan_parameter_salah_ditolak(self):
        kapal, kendaraan = baca_data()
        for parameter in (dict(daftar_seed=[]), dict(daftar_seed=[42, 42]),
                          dict(daftar_seed=[True]), dict(parameter=[])):
            with tempfile.TemporaryDirectory() as tmp:
                tujuan = Path(tmp) / "uji"
                with self.subTest(parameter=parameter), self.assertRaises(ValueError):
                    jalankan(None, kapal, kendaraan, tujuan, **parameter)
                self.assertFalse(tujuan.exists())

    def test_generator_dari_luar_bisa_dipakai_dan_dicatat_runner(self):
        kapal, kendaraan = baca_data()

        def generator_bersama(kapal, kendaraan, state, acak):
            return None

        with tempfile.TemporaryDirectory() as tmp:
            tujuan = Path(tmp) / "sa"
            jalankan(cari_sa, kapal, kendaraan, tujuan, daftar_seed=[42], grafik=False,
                     parameter=dict(tetangga=generator_bersama, batas_iterasi=2, cek_stuck=None))
            hasil = baca_json(tujuan / "ulangan_1_seed_42/hasil.json")
            self.assertEqual(hasil["parameter"]["tetangga"], "generator_bersama")
            self.assertEqual(hasil["metrik"]["jumlah_tanpa_kandidat"], 2)
            self.assertIsNone(hasil["metrik"]["frekuensi_stuck"])

    @unittest.skipUnless(importlib.util.find_spec("matplotlib"), "Matplotlib belum tersedia")
    def test_cli_sa_menyimpan_hasil_dan_grafik_dengan_generator_asli(self):
        from matplotlib.image import imread

        with tempfile.TemporaryDirectory() as tmp:
            tujuan = Path(tmp) / "sa"
            proses = subprocess.run(
                [sys.executable, "-m", "src.eksperimen", "--output", str(tujuan),
                 "--parameter", json.dumps(dict(batas_iterasi=15, interval_stuck=5))],
                cwd=ROOT, capture_output=True, text=True, timeout=60)
            self.assertEqual(proses.returncode, 0, proses.stderr)
            folder = sorted(tujuan.glob("ulangan_*"))
            self.assertEqual(len(folder), 3)
            for ulangan in folder:
                hasil = baca_json(ulangan / "hasil.json")
                self.assertEqual(hasil["objektif"], "jumlah tarif_kirim")
                self.assertEqual(hasil["jumlah_iterasi"], 15)
                self.assertEqual(hasil["satuan_objektif"], "juta rupiah")
                self.assertEqual(hasil["metrik"]["generator_tetangga"], "tetangga_acak")
                self.assertEqual(hasil["metrik"]["jumlah_pemeriksaan"], 3)
                self.assertGreaterEqual(hasil["objektif_akhir"], hasil["objektif_awal"])
                gambar = list(ulangan.glob("*.png"))
                self.assertEqual(len(gambar), 4)
                for berkas in gambar:
                    self.assertGreater(imread(berkas).size, 0)
            self.assertTrue((tujuan / "ringkasan.csv").is_file())
