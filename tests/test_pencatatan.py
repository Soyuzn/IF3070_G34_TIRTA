import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.pencatatan import (periksa_riwayat, simpan_percobaan, ukur_pencarian)


class UjiPencatatan(unittest.TestCase):
    def setUp(self):
        self.kapal = [dict(id="k", lebar=2, panjang=2, kapasitas=3)]
        self.kendaraan = [dict(id="a", lebar=1, panjang=2, tarif_kirim=10, berat=2, eta_hari=0)]
        self.state = dict(a=dict(kapal_id="k", x=0, y=0, orientasi="vertikal"))
        self.kwargs = dict(algoritma="uji", seed=42, parameter={"batas_iterasi": 1},
                           kapal=self.kapal, kendaraan=self.kendaraan,
                           state_awal=dict(a=None), state_akhir=self.state,
                           durasi_detik=.25, riwayat=[dict(iterasi=0, objektif=0),
                                                     dict(iterasi=1, objektif=10)],
                           metrik={"catatan": "ILUSTRASI"}, ilustrasi=True)

    def test_snapshot_json_csv_dan_tidak_menimpa(self):
        with tempfile.TemporaryDirectory() as tmp:
            tujuan = simpan_percobaan(Path(tmp) / "run", **self.kwargs)
            hasil = json.loads((tujuan / "hasil.json").read_text())
            self.assertEqual(hasil["state_akhir"], self.state)
            self.assertEqual(hasil["objektif_akhir"], 10)
            self.assertEqual(hasil["durasi_detik"], .25)
            self.assertEqual(hasil["riwayat"], self.kwargs["riwayat"])
            self.assertIsNone(hasil["state_awal"]["a"])
            with (tujuan / "riwayat.csv").open(newline="") as f:
                baris = list(csv.DictReader(f))
            self.assertEqual(baris[1]["objektif"], "10")
            self.assertEqual(baris[1]["eksponen_penerimaan"], "")
            with self.assertRaises(FileExistsError):
                simpan_percobaan(tujuan, **self.kwargs)

    def test_data_rusak_tidak_membuat_folder(self):
        for perubahan in (dict(durasi_detik=float("nan")), dict(durasi_detik=-1),
                          dict(seed=True), dict(parameter={"x": float("inf")}),
                          dict(state_akhir={}), dict(riwayat=[])):
            with tempfile.TemporaryDirectory() as tmp:
                tujuan = Path(tmp) / "run"
                with self.subTest(perubahan=perubahan), self.assertRaises(ValueError):
                    simpan_percobaan(tujuan, **dict(self.kwargs, **perubahan))
                self.assertFalse(tujuan.exists())

    def test_bonus_eta_tersimpan_dengan_nilai_dan_satuan_yang_sesuai(self):
        kendaraan = [dict(self.kendaraan[0], eta_hari=3)]
        riwayat = [dict(iterasi=0, objektif=0), dict(iterasi=1, objektif=2.5)]
        argumen = dict(self.kwargs, kendaraan=kendaraan, riwayat=riwayat)
        with tempfile.TemporaryDirectory() as tmp:
            tujuan = simpan_percobaan(Path(tmp) / "eta", objektif="tarif_eta", **argumen)
            hasil = json.loads((tujuan / "hasil.json").read_text())
            self.assertEqual(hasil["objektif_akhir"], 2.5)
            self.assertEqual(hasil["satuan_objektif"], "juta rupiah berbobot ETA")
            self.assertEqual(hasil["objektif"], "tarif_kirim / (1 + eta_hari)")

    def test_riwayat_sa_ga_dan_restart(self):
        periksa_riwayat([dict(iterasi=0, maksimum_populasi=10, rata_rata_populasi=5),
                         dict(iterasi=1, maksimum_populasi=12, rata_rata_populasi=9)])
        periksa_riwayat([dict(iterasi=0, objektif=10, restart=0),
                         dict(iterasi=1, objektif=8, eksponen_penerimaan=.5, restart=1)])
        for riwayat in ([dict(iterasi=1, objektif=2)], [dict(iterasi=0)],
                        [dict(iterasi=0, objektif=float("inf"))],
                        [dict(iterasi=0, maksimum_populasi=2, rata_rata_populasi=3)],
                        [dict(iterasi=0, maksimum_populasi=2)],
                        [dict(iterasi=0, objektif=1, asing=0)],
                        [dict(iterasi=0, objektif=1), dict(iterasi=0, objektif=1)]):
            with self.subTest(riwayat=riwayat), self.assertRaises(ValueError):
                periksa_riwayat(riwayat)

    def test_timer_mengukur_pemanggilan_saja(self):
        kejadian = []
        def jam():
            kejadian.append("jam")
            return {1: 100, 3: 100.75}[len(kejadian)]
        def pencarian(x):
            kejadian.append("pencarian")
            return x + 1
        with patch("src.pencatatan.perf_counter", side_effect=jam):
            hasil, durasi = ukur_pencarian(pencarian, 4)
        self.assertEqual((hasil, durasi), (5, .75))
        self.assertEqual(kejadian, ["jam", "pencarian", "jam"])


if __name__ == "__main__":
    unittest.main()
