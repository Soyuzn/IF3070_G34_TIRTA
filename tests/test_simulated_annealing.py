"""Uji logika SA dengan kandidat terkontrol, bukan generator pengganti Orang 1."""
import copy
import json
import math
import random
import unittest

from src.simulated_annealing import _jadwal_suhu, cari, probabilitas_penerimaan
from src.data import baca_data, inisialisasi_acak, nilai_objektif, periksa_state


class UjiSA(unittest.TestCase):
    def setUp(self):
        self.kapal = [dict(id="k", lebar=2, panjang=1, kapasitas=2)]
        self.kendaraan = [
            dict(id="a", lebar=1, panjang=1, berat=1, tarif_kirim=10, eta_hari=0),
            dict(id="b", lebar=1, panjang=1, berat=1, tarif_kirim=20, eta_hari=3),
        ]
        posisi = dict(kapal_id="k", x=0, y=0, orientasi="vertikal")
        self.kosong = dict(a=None, b=None)
        self.a = dict(a=posisi, b=None)
        self.b = dict(a=None, b=posisi)
        self.penuh = dict(a=posisi, b=dict(posisi, x=1))

    def urutan(self, *daftar_state):
        kandidat = iter(daftar_state)

        def berikutnya(kapal, kendaraan, state, acak):
            baru = copy.deepcopy(next(kandidat, None))
            return None if baru is None else (baru, ("uji",))

        return berikutnya

    def test_peluang_dan_pengaruh_bias(self):
        self.assertEqual(probabilitas_penerimaan(1, 2), 1)
        self.assertEqual(probabilitas_penerimaan(0, 2), 1)
        self.assertAlmostEqual(probabilitas_penerimaan(-2, 2), math.exp(-1))
        self.assertLess(probabilitas_penerimaan(-2, 2, 2),
                        probabilitas_penerimaan(-2, 2, .5))

    def test_jadwal_suhu_sesuai_schedule_pada_buku(self):
        self.assertEqual([_jadwal_suhu(t, 8, .5, 2) for t in range(1, 5)], [8, 4, 2, 0])

    def test_penurunan_bisa_ditolak_dan_nilai_sama_diterima(self):
        akhir, riwayat, metrik = cari(
            self.kapal, self.kendaraan, self.b, 42, batas_iterasi=2,
            suhu_awal=.1, suhu_minimum=.01, tetangga=self.urutan(self.a, self.b))
        self.assertEqual(akhir, self.b)
        self.assertEqual([b["objektif"] for b in riwayat], [20, 20, 20])
        self.assertEqual([b["diterima"] for b in metrik["langkah_sa"]], [False, True])

    def test_iterasi_nol_tidak_memanggil_generator(self):
        def tidak_dipanggil(*args):
            self.fail("Tidak boleh mencari tetangga saat batas_iterasi=0")

        akhir, riwayat, metrik = cari(
            self.kapal, self.kendaraan, self.a, 42, batas_iterasi=0,
            tetangga=tidak_dipanggil)
        self.assertEqual(akhir, self.a)
        self.assertEqual(riwayat, [dict(iterasi=0, objektif=10)])
        self.assertEqual(metrik["langkah_sa"], [])

    def test_state_terbaik_disimpan_dan_input_tidak_berubah(self):
        sebelum = copy.deepcopy((self.kapal, self.kendaraan, self.b))
        rng = random.getstate()
        akhir, riwayat, metrik = cari(
            self.kapal, self.kendaraan, self.b, 1, batas_iterasi=2,
            suhu_awal=1e10, tetangga=self.urutan(self.a, self.kosong))
        self.assertEqual(akhir, self.b)
        self.assertEqual([b["objektif"] for b in riwayat], [20, 10, 0])
        self.assertEqual(metrik["jumlah_diterima"], 2)
        self.assertEqual((self.kapal, self.kendaraan, self.b), sebelum)
        self.assertEqual(random.getstate(), rng)

    def test_perbaikan_selalu_diterima_dan_eksponen_boleh_melebihi_satu(self):
        akhir, riwayat, metrik = cari(
            self.kapal, self.kendaraan, self.kosong, 1, batas_iterasi=2,
            suhu_awal=1, tetangga=self.urutan(self.a, self.penuh))
        self.assertEqual(akhir, self.penuh)
        self.assertEqual(riwayat[-1]["objektif"], 30)
        self.assertGreater(riwayat[1]["eksponen_penerimaan"], 1)
        self.assertEqual(metrik["langkah_sa"][0]["probabilitas_penerimaan"], 1)

    def test_overflow_tidak_memalsukan_eksponen_atau_merusak_json(self):
        kendaraan = [dict(self.kendaraan[0], tarif_kirim=1000)]
        akhir, riwayat, metrik = cari(
            self.kapal, kendaraan, {"a": None}, 1, batas_iterasi=1,
            tetangga=self.urutan({"a": self.a["a"]}), suhu_awal=.1)
        self.assertIsNotNone(akhir["a"])
        self.assertIsNone(riwayat[-1]["eksponen_penerimaan"])
        self.assertEqual(metrik["jumlah_eksponen_overflow"], 1)
        json.dumps((akhir, riwayat, metrik), allow_nan=False)

    def test_sampling_gagal_bukan_bukti_stuck(self):
        _, riwayat, metrik = cari(
            self.kapal, self.kendaraan, self.kosong, 1, batas_iterasi=20,
            suhu_awal=8, suhu_minimum=2, pendinginan=.5, tetangga=self.urutan())
        self.assertEqual(riwayat[-1]["iterasi"], 3)
        self.assertEqual(metrik["alasan_berhenti"], "suhu_minimum")
        self.assertEqual(metrik["jumlah_tanpa_kandidat"], 3)
        self.assertEqual(metrik["frekuensi_stuck"], 0)
        self.assertEqual(metrik["pemeriksaan_stuck"], [dict(iterasi=3, stuck=False)])

    def test_pencatatan_checkpoint_memakai_hasil_pemeriksa_yang_diberikan(self):
        jawaban = iter([True, False, True])
        _, _, metrik = cari(
            self.kapal, self.kendaraan, self.penuh, 42, batas_iterasi=5,
            interval_stuck=2, tetangga=self.urutan(), cek_stuck=lambda *_: next(jawaban))
        self.assertEqual([p["iterasi"] for p in metrik["pemeriksaan_stuck"]], [2, 4, 5])
        self.assertEqual(metrik["jumlah_stuck"], 2)
        self.assertAlmostEqual(metrik["frekuensi_stuck"], 2 / 3)

    def test_generator_tidak_valid_ditolak(self):
        with self.assertRaisesRegex(ValueError, "tetangga harus berupa fungsi"):
            cari(self.kapal, self.kendaraan, self.a, 42, tetangga=None)

    def test_generator_asli_deterministik_dan_state_valid(self):
        kapal, kendaraan = baca_data()
        for seed in (40, 41, 42):
            awal = inisialisasi_acak(kapal, kendaraan, seed)
            sebelum, rng = copy.deepcopy(awal), random.getstate()
            pertama = cari(kapal, kendaraan, awal, seed, batas_iterasi=100)
            self.assertEqual(pertama, cari(kapal, kendaraan, awal, seed, batas_iterasi=100))
            tanpa_cek = cari(kapal, kendaraan, awal, seed, batas_iterasi=100, cek_stuck=None)
            self.assertEqual(pertama[:2], tanpa_cek[:2])
            self.assertEqual(pertama[2]["langkah_sa"], tanpa_cek[2]["langkah_sa"])
            akhir, riwayat, metrik = pertama
            periksa_state(kapal, kendaraan, akhir)
            self.assertGreaterEqual(nilai_objektif(kapal, kendaraan, akhir),
                                    nilai_objektif(kapal, kendaraan, awal))
            self.assertEqual(awal, sebelum)
            self.assertEqual(random.getstate(), rng)
            self.assertEqual(riwayat[-1]["iterasi"], 100)
            self.assertEqual(metrik["jumlah_pemeriksaan"], 2)
            self.assertEqual(metrik["generator_tetangga"], "tetangga_acak")
            self.assertTrue(all(b["langkah"][0] in ("pindah", "putar", "tukar")
                                for b in metrik["langkah_sa"] if b["langkah"] is not None))

    def test_stuck_bisa_dinonaktifkan_dan_state_kosong_aman(self):
        akhir, riwayat, metrik = cari(self.kapal, [], {}, 42, batas_iterasi=2)
        self.assertEqual(akhir, {})
        self.assertEqual(riwayat[-1]["iterasi"], 2)
        self.assertEqual(metrik["jumlah_tanpa_kandidat"], 2)
        self.assertEqual(metrik["frekuensi_stuck"], 1)
        _, _, metrik = cari(self.kapal, [], {}, 42, batas_iterasi=1, cek_stuck=None)
        self.assertIsNone(metrik["frekuensi_stuck"])

    def test_parameter_salah_dan_kandidat_invalid_ditolak(self):
        for parameter in (dict(seed=True), dict(suhu_awal=0), dict(suhu_awal=True),
                          dict(pendinginan=1), dict(pendinginan=0), dict(suhu_minimum=100),
                          dict(evaluation_bias=0), dict(evaluation_bias=float("inf")),
                          dict(batas_iterasi=-1), dict(batas_iterasi=True),
                          dict(interval_stuck=0), dict(tetangga=None), dict(cek_stuck=1),
                          dict(objektif="tarif_eta")):
            argumen = dict(seed=1, batas_iterasi=1, tetangga=self.urutan())
            argumen.update(parameter)
            with self.subTest(parameter=parameter), self.assertRaises(ValueError):
                cari(self.kapal, self.kendaraan, self.a, **argumen)
        with self.assertRaises(ValueError):
            cari(self.kapal, self.kendaraan, self.a, 1, batas_iterasi=1,
                 tetangga=self.urutan(dict(a=self.a["a"], b=self.a["a"])))
        with self.assertRaisesRegex(ValueError, "cek_stuck harus mengembalikan bool"):
            cari(self.kapal, self.kendaraan, self.a, 1, batas_iterasi=1,
                 tetangga=self.urutan(), cek_stuck=lambda *_: None)
