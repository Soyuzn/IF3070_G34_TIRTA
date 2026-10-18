"""Uji alur dataset, demo CLI, penyimpanan, dan visualisasi secara bersama."""
import csv
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.data import baca_data, baca_json, inisialisasi_acak, nilai_objektif, periksa_state
from src.pencatatan import simpan_percobaan

ROOT = Path(__file__).resolve().parents[1]


class UjiIntegrasi(unittest.TestCase):
    def jalankan_demo(self, nama_kapal, tujuan, grafik=False, objektif="tarif_kirim"):
        perintah = [sys.executable, "-m", "src.contoh", "--kapal",
                    f"data/{nama_kapal}", "--output", str(tujuan), "--objektif", objektif]
        if not grafik:
            perintah.append("--tanpa-grafik")
        proses = subprocess.run(perintah, cwd=ROOT, capture_output=True, text=True, timeout=60)
        self.assertEqual(proses.returncode, 0, proses.stderr)
        self.assertIn("ILUSTRASI", proses.stdout)
        return baca_json(tujuan / "hasil.json")

    def test_demo_cli_sesuai_dataset_dan_contoh_repo(self):
        for nama_kapal, objektif in (("kapal.json", 414), ("kapal_bonus.json", 731)):
            with self.subTest(kapal=nama_kapal), tempfile.TemporaryDirectory() as tmp:
                tujuan = Path(tmp) / "demo"
                hasil = self.jalankan_demo(nama_kapal, tujuan)
                kapal, kendaraan = baca_data(
                    ROOT / "data" / nama_kapal, ROOT / "data/kendaraan.json")
                self.assertEqual((hasil["kapal"], hasil["kendaraan"]), (kapal, kendaraan))
                for nama_state in ("state_awal", "state_akhir"):
                    periksa_state(kapal, kendaraan, hasil[nama_state])
                    self.assertEqual(nilai_objektif(kapal, kendaraan, hasil[nama_state]), objektif)
                self.assertEqual(hasil["state_awal"], hasil["state_akhir"])
                self.assertEqual(hasil["durasi_detik"], 0)
                self.assertTrue(hasil["ilustrasi"])
                with (tujuan / "riwayat.csv").open(newline="", encoding="utf-8") as berkas:
                    riwayat = list(csv.DictReader(berkas))
                self.assertEqual(riwayat[0]["objektif"], str(hasil["riwayat"][0]["objektif"]))
                self.assertEqual(riwayat[0]["eksponen_penerimaan"], "")
                if nama_kapal == "kapal.json":
                    self.assertEqual(hasil, baca_json(ROOT / "output/ilustrasi_data/hasil.json"))
                    self.assertEqual((tujuan / "riwayat.csv").read_bytes(),
                                     (ROOT / "output/ilustrasi_data/riwayat.csv").read_bytes())

    @unittest.skipUnless(importlib.util.find_spec("matplotlib"), "Matplotlib belum tersedia")
    def test_demo_cli_menghasilkan_lima_grafik_yang_bisa_dibaca(self):
        from matplotlib.image import imread

        nama_gambar = {"state_awal.png", "state_akhir.png", "objektif.png",
                       "penerimaan_sa_ilustrasi.png", "populasi_ga_ilustrasi.png"}
        skenario = [("kapal.json", "tarif_kirim"), ("kapal_bonus.json", "tarif_kirim"),
                    ("kapal_bonus.json", "tarif_eta")]
        for nama_kapal, objektif in skenario:
            with self.subTest(kapal=nama_kapal, objektif=objektif):
                with tempfile.TemporaryDirectory() as tmp:
                    tujuan = Path(tmp) / "demo"
                    hasil = self.jalankan_demo(nama_kapal, tujuan, True, objektif)
                    self.assertEqual({p.name for p in tujuan.glob("*.png")}, nama_gambar)
                    if objektif == "tarif_eta":
                        self.assertEqual(hasil["satuan_objektif"], "juta rupiah berbobot ETA")
                        nilai = sum(k["tarif_kirim"] / (1 + k["eta_hari"])
                                    for k in hasil["kendaraan"]
                                    if hasil["state_akhir"][k["id"]] is not None)
                        self.assertAlmostEqual(hasil["objektif_akhir"], nilai)
                    for nama in nama_gambar:
                        gambar = imread(tujuan / nama)
                        self.assertGreater(gambar.size, 0)
                        self.assertGreater(float(gambar.max() - gambar.min()), 0)

    def test_populasi_ga_tetap_utuh_setelah_disimpan(self):
        kapal, kendaraan = baca_data(ROOT / "data/kapal_bonus.json", ROOT / "data/kendaraan.json")
        populasi = [inisialisasi_acak(kapal, kendaraan, seed) for seed in (40, 41, 42)]
        nilai = [nilai_objektif(kapal, kendaraan, state) for state in populasi]
        terbaik = populasi[nilai.index(max(nilai))]
        riwayat = [{"iterasi": 0, "maksimum_populasi": max(nilai),
                    "rata_rata_populasi": sum(nilai) / len(nilai)}]
        with tempfile.TemporaryDirectory() as tmp:
            tujuan = simpan_percobaan(
                Path(tmp) / "ga", algoritma="ilustrasi_populasi_ga", seed=40,
                parameter={"jumlah_populasi": 3, "batas_iterasi": 0},
                kapal=kapal, kendaraan=kendaraan, state_awal=terbaik, state_akhir=terbaik,
                durasi_detik=0, riwayat=riwayat, ilustrasi=True,
                metrik={"populasi_awal": populasi, "populasi_akhir": populasi})
            hasil = baca_json(tujuan / "hasil.json")
            self.assertEqual(hasil["objektif_akhir"], max(nilai))
            self.assertEqual(hasil["riwayat"], riwayat)
            for nama in ("populasi_awal", "populasi_akhir"):
                self.assertEqual(hasil["metrik"][nama], populasi)
                for state in hasil["metrik"][nama]:
                    periksa_state(kapal, kendaraan, state)
