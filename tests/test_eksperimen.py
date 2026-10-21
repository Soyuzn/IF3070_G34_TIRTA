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

        def cari(kapal, kendaraan, state, seed, objektif, **parameter):
            kejadian.append("cari")
            nilai = nilai_objektif(kapal, kendaraan, state, objektif)
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
                self.assertFalse(data["ilustrasi"])
                self.assertEqual(data["durasi_detik"], 2)
            with (tujuan / "ringkasan.csv").open(newline="") as berkas:
                self.assertEqual(len(list(csv.DictReader(berkas))), 3)
            self.assertTrue((tujuan / "ringkasan.md").exists())
            with self.assertRaises(FileExistsError):
                jalankan(cari, kapal, kendaraan, tujuan, grafik=False)

    def test_hook_populasi_dijalankan_sebelum_timer(self):
        kapal, kendaraan = baca_data()
        kejadian = []

        def siapkan(kapal, kendaraan, seed, parameter):
            kejadian.append("siapkan")
            state = inisialisasi_acak(kapal, kendaraan, seed)
            return state, dict(parameter, populasi_awal=[state])

        def cari(kapal, kendaraan, state, seed, objektif, populasi_awal):
            kejadian.append("cari")
            self.assertEqual(populasi_awal, [state])
            nilai = nilai_objektif(kapal, kendaraan, state, objektif)
            return state, [dict(iterasi=0, maksimum_populasi=nilai,
                                rata_rata_populasi=nilai)], {}

        with tempfile.TemporaryDirectory() as tmp:
            with patch("src.pencatatan.perf_counter", side_effect=[0, 1]):
                jalankan(cari, kapal, kendaraan, Path(tmp) / "uji", daftar_seed=[42],
                         siapkan=siapkan, grafik=False, algoritma="uji_hook_ga")
        self.assertEqual(kejadian, ["siapkan", "cari"])

    def test_seed_duplikat_dan_parameter_salah_ditolak(self):
        kapal, kendaraan = baca_data()
        for parameter in (dict(daftar_seed=[]), dict(daftar_seed=[42, 42]),
                          dict(daftar_seed=[True]), dict(parameter=[]), dict(objektif="asing")):
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
                self.assertFalse(hasil["ilustrasi"])
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

    def test_bonus_ditolak_runner_dan_cli(self):
        kapal, kendaraan = baca_data()
        with tempfile.TemporaryDirectory() as tmp:
            tujuan = Path(tmp) / "uji"
            with self.assertRaisesRegex(ValueError, "hanya tarif_kirim"):
                jalankan(cari_sa, kapal, kendaraan, tujuan, objektif="tarif_eta")
            for modul in ("src.eksperimen", "src.contoh"):
                proses = subprocess.run(
                    [sys.executable, "-m", modul, "--output", str(tujuan),
                     "--objektif", "tarif_eta"], cwd=ROOT, capture_output=True,
                    text=True, timeout=60)
                self.assertEqual(proses.returncode, 2, proses.stderr)
                self.assertIn("invalid choice", proses.stderr)
            self.assertFalse(tujuan.exists())
