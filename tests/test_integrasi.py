"""Uji CLI GA, pencatatan, dan pembuatan gambar PNG."""
import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.data import baca_data, baca_json, inisialisasi_acak, nilai_objektif, periksa_state
from src.pencatatan import simpan_percobaan

ROOT = Path(__file__).resolve().parents[1]


class UjiIntegrasi(unittest.TestCase):
    def test_ga_cli_menyimpan_populasi_dan_gambar(self):
        with tempfile.TemporaryDirectory() as tmp:
            tujuan = Path(tmp) / "ga"
            perintah = [sys.executable, "-m", "src.genetic",
                        "--jumlah-populasi", "5", "--batas-iterasi", "4",
                        "--output", str(tujuan)]
            proses = subprocess.run(perintah, cwd=ROOT, capture_output=True,
                                    text=True, timeout=60)
            self.assertEqual(proses.returncode, 0, proses.stderr)
            self.assertEqual({p.name for p in tujuan.iterdir()},
                             {"hasil.json", "riwayat.csv", "state_awal.png",
                              "state_akhir.png", "objektif.png"})
            for gambar in tujuan.glob("*.png"):
                self.assertTrue(gambar.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
            hasil = baca_json(tujuan / "hasil.json")
            self.assertEqual(hasil["algoritma"], "genetic_algorithm")
            self.assertEqual(len(hasil["kapal"]), 1)
            self.assertEqual(hasil["objektif"], "jumlah tarif_kirim")
            self.assertEqual(hasil["satuan_objektif"], "juta rupiah")
            self.assertEqual(hasil["jumlah_iterasi"], 4)
            self.assertEqual(len(hasil["riwayat"]), 5)
            for tahap, baris in (("awal", hasil["riwayat"][0]),
                                 ("akhir", hasil["riwayat"][-1])):
                populasi = hasil["metrik"][f"populasi_{tahap}"]
                self.assertEqual(len(populasi), 5)
                nilai = [nilai_objektif(hasil["kapal"], hasil["kendaraan"], p)
                         for p in populasi]
                self.assertAlmostEqual(hasil[f"objektif_{tahap}"], max(nilai))
                self.assertAlmostEqual(baris["maksimum_populasi"], max(nilai))
                self.assertAlmostEqual(baris["rata_rata_populasi"], sum(nilai) / len(nilai))
            with (tujuan / "riwayat.csv").open(newline="", encoding="utf-8") as berkas:
                riwayat = list(csv.DictReader(berkas))
            self.assertEqual(len(riwayat), 5)
            self.assertEqual(float(riwayat[-1]["maksimum_populasi"]), hasil["objektif_akhir"])
            self.assertEqual(riwayat[-1]["eksponen_penerimaan"], "")

    def test_populasi_ga_tetap_utuh_setelah_disimpan(self):
        kapal, kendaraan = baca_data(ROOT / "data/kapal.json", ROOT / "data/kendaraan.json")
        populasi = [inisialisasi_acak(kapal, kendaraan, seed) for seed in (40, 41, 42)]
        nilai = [nilai_objektif(kapal, kendaraan, state) for state in populasi]
        terbaik = populasi[nilai.index(max(nilai))]
        riwayat = [{"iterasi": 0, "maksimum_populasi": max(nilai),
                    "rata_rata_populasi": sum(nilai) / len(nilai)}]
        with tempfile.TemporaryDirectory() as tmp:
            tujuan = simpan_percobaan(
                Path(tmp) / "ga", algoritma="uji_ga", seed=40,
                parameter={"jumlah_populasi": 3, "batas_iterasi": 0},
                kapal=kapal, kendaraan=kendaraan, state_awal=terbaik, state_akhir=terbaik,
                durasi_detik=0, riwayat=riwayat,
                metrik={"populasi_awal": populasi, "populasi_akhir": populasi})
            hasil = baca_json(tujuan / "hasil.json")
            self.assertEqual(hasil["objektif_akhir"], max(nilai))
            self.assertEqual(hasil["riwayat"], riwayat)
            for nama in ("populasi_awal", "populasi_akhir"):
                self.assertEqual(hasil["metrik"][nama], populasi)
                for state in hasil["metrik"][nama]:
                    periksa_state(kapal, kendaraan, state)
