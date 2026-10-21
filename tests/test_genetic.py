import random
import unittest
from copy import deepcopy

from src.data import nilai_objektif, periksa_state
from src.genetic import cari, kawin_silang, mutasi, perbaiki, pilih_induk
from src.pencatatan import periksa_riwayat


class UjiGenetika(unittest.TestCase):
    def setUp(self):
        self.kapal = [dict(id="dek", lebar=2, panjang=1, kapasitas=2)]
        self.kendaraan = [dict(id=id, lebar=1, panjang=1, berat=1,
                               tarif_kirim=tarif, eta_hari=eta)
                          for id, tarif, eta in (("a", 10, 0), ("b", 20, 2), ("c", 30, 4))]
        self.kosong = dict.fromkeys(("a", "b", "c"))
        self.induk_a = dict(a=self.posisi(0), b=self.posisi(1), c=None)
        self.induk_b = dict(a=None, b=self.posisi(0), c=self.posisi(1))

    def posisi(self, x, kapal_id="dek"):
        return dict(kapal_id=kapal_id, x=x, y=0, orientasi="vertikal")

    def test_rolet_mengikuti_fitness_dan_bisa_semua_nol(self):
        acak = random.Random(42)
        terpilih = [p for _ in range(1000) for p in pilih_induk(["a", "b"], [1, 9], acak)]
        self.assertTrue(0.85 < terpilih.count("b") / len(terpilih) < 0.95)
        self.assertEqual(pilih_induk(["a", "b"], [0, 1], acak), ["b", "b"])
        terpilih = [p for _ in range(30) for p in pilih_induk(["a", "b"], [0, 0], acak)]
        self.assertEqual(set(terpilih), {"a", "b"})

    def test_kawin_silang_memperbaiki_tabrakan_tanpa_mengubah_induk(self):
        sebelum = deepcopy((self.induk_a, self.induk_b))
        ada_gabungan = False
        for seed in range(20):
            anak = kawin_silang(self.kapal, self.kendaraan, self.induk_a,
                                self.induk_b, random.Random(seed))
            for state in anak:
                periksa_state(self.kapal, self.kendaraan, state)
                ada_gabungan |= state not in sebelum
                for id, posisi in state.items():
                    self.assertIn(posisi, (None, self.induk_a[id], self.induk_b[id]))
        self.assertTrue(ada_gabungan)
        self.assertEqual((self.induk_a, self.induk_b), sebelum)
        anak[0]["a"] = None
        self.assertEqual((self.induk_a, self.induk_b), sebelum)

    def test_perbaikan_kapasitas_dan_mutasi_valid(self):
        kapal = [dict(self.kapal[0], kapasitas=1)]
        hasil = perbaiki(kapal, self.kendaraan, self.induk_a, random.Random(42))
        periksa_state(kapal, self.kendaraan, hasil)
        self.assertEqual(sum(p is not None for p in hasil.values()), 1)
        sebelum = deepcopy(self.induk_a)
        self.assertEqual(mutasi(self.kapal, self.kendaraan, sebelum, random.Random(0), 0),
                         sebelum)
        berubah = 0
        for seed in range(20):
            hasil = mutasi(self.kapal, self.kendaraan, self.induk_a, random.Random(seed), 1)
            periksa_state(self.kapal, self.kendaraan, hasil)
            berubah += hasil != self.induk_a
        self.assertGreater(berubah, 0)
        self.assertEqual(self.induk_a, sebelum)
        hasil = mutasi(self.kapal, self.kendaraan, self.kosong, random.Random(42), 1)
        self.assertGreater(nilai_objektif(self.kapal, self.kendaraan, hasil), 0)

    def test_pencarian_bisa_diulang_dan_menyimpan_populasi(self):
        sebelum = deepcopy((self.kapal, self.kendaraan, self.induk_a))
        rng_global = random.getstate()
        argumen = dict(seed=42, jumlah_populasi=5, batas_iterasi=8, peluang_mutasi=1)
        hasil = cari(self.kapal, self.kendaraan, self.induk_a, **argumen)
        self.assertEqual(hasil, cari(self.kapal, self.kendaraan, self.induk_a, **argumen))
        self.assertEqual(random.getstate(), rng_global)
        self.assertEqual((self.kapal, self.kendaraan, self.induk_a), sebelum)
        akhir, riwayat, metrik = hasil
        periksa_riwayat(riwayat)
        self.assertEqual([b["iterasi"] for b in riwayat], list(range(9)))
        maksimum = [b["maksimum_populasi"] for b in riwayat]
        self.assertEqual(maksimum, sorted(maksimum))
        self.assertEqual(nilai_objektif(self.kapal, self.kendaraan, akhir), maksimum[-1])
        for nama, baris in (("populasi_awal", riwayat[0]), ("populasi_akhir", riwayat[-1])):
            populasi = metrik[nama]
            self.assertEqual(len(populasi), 5)
            nilai = [nilai_objektif(self.kapal, self.kendaraan, p) for p in populasi]
            self.assertEqual(baris["maksimum_populasi"], max(nilai))
            self.assertEqual(baris["rata_rata_populasi"], sum(nilai) / len(nilai))
        self.assertEqual(metrik["populasi_awal"][0], self.induk_a)
        simpanan = deepcopy(metrik)
        akhir["a"] = self.posisi(99)
        self.assertEqual(metrik, simpanan)

    def test_nol_iterasi_mengembalikan_terbaik_populasi_awal(self):
        akhir, riwayat, metrik = cari(self.kapal, self.kendaraan, self.induk_a, 42,
                                     jumlah_populasi=3, batas_iterasi=0)
        self.assertEqual(len(riwayat), 1)
        nilai = [nilai_objektif(self.kapal, self.kendaraan, p)
                 for p in metrik["populasi_awal"]]
        self.assertAlmostEqual(riwayat[0]["maksimum_populasi"], max(nilai))
        self.assertEqual(nilai_objektif(self.kapal, self.kendaraan, akhir), max(nilai))
        self.assertEqual(metrik["populasi_awal"], metrik["populasi_akhir"])

    def test_kasus_kosong_satu_kendaraan_dan_parameter_salah(self):
        akhir, riwayat, _ = cari(self.kapal, [], {}, 42, batas_iterasi=2)
        self.assertEqual(akhir, {})
        self.assertTrue(all(b["maksimum_populasi"] == 0 for b in riwayat))
        anak = kawin_silang(self.kapal, self.kendaraan[:1], {"a": None},
                            {"a": self.posisi(0)}, random.Random(42))
        self.assertEqual(anak, ({"a": None}, {"a": self.posisi(0)}))
        for parameter in (dict(jumlah_populasi=1), dict(jumlah_populasi=True),
                          dict(batas_iterasi=-1), dict(batas_iterasi=1.5),
                          dict(seed=True),
                          dict(peluang_mutasi=-0.1), dict(peluang_mutasi=float("nan")),
                          dict(peluang_mutasi=1.1)):
            with self.subTest(parameter=parameter), self.assertRaises(ValueError):
                cari(self.kapal, self.kendaraan, self.kosong, **({"seed": 42} | parameter))
