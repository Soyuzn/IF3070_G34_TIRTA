import copy
import random
import unittest
from itertools import combinations, product
from pathlib import Path

from src.data import baca_data, inisialisasi_acak, nilai_objektif, periksa_state, ukuran
from src.tetangga import ORIENTASI, _terapkan, _valid, puncak_lokal, semua_tetangga, tetangga_acak

ROOT = Path(__file__).resolve().parents[1]


class UjiTetangga(unittest.TestCase):
    def test_tetangga_acak_valid_dan_state_asli_utuh(self):
        kapal, kendaraan = baca_data(ROOT / "data/kapal.json", ROOT / "data/kendaraan.json")
        for seed in range(50):
            with self.subTest(seed=seed):
                state = inisialisasi_acak(kapal, kendaraan, seed)
                salinan = copy.deepcopy(state)
                baru, langkah = tetangga_acak(kapal, kendaraan, state, random.Random(seed))
                self.assertEqual(state, salinan)
                self.assertNotEqual(baru, state)
                self.assertIn(langkah[0], ("pindah", "putar", "tukar"))
                periksa_state(kapal, kendaraan, baru)
                for posisi in baru.values():
                    if posisi is not None:
                        posisi["x"] = -1
                self.assertEqual(state, salinan)

    def test_semua_tetangga_sama_dengan_cek_penuh(self):
        kapal, kendaraan = baca_data(ROOT / "data/kapal.json", ROOT / "data/kendaraan.json")
        state, dek = inisialisasi_acak(kapal, kendaraan, 42), kapal[0]
        posisi = [None] + [dict(kapal_id=dek["id"], x=x, y=y, orientasi=o) for o, x, y in
                           product(ORIENTASI, range(dek["lebar"]), range(dek["panjang"]))]
        calon = [("pindah", i, p) for i in state for p in posisi]
        calon += [("putar", i) for i in state if state[i] is not None]
        calon += [("tukar", a, b) for a, b in combinations(state, 2)]
        harapan = [l for l in calon if (lambda b: b != state and _valid(kapal, kendaraan, b))(
            _terapkan(state, l))]
        hasil = list(semua_tetangga(kapal, kendaraan, state))
        self.assertEqual(sorted(map(repr, harapan)), sorted(repr(l) for _, l in hasil))
        for baru, langkah in hasil[:20]:
            self.assertEqual(baru, _terapkan(state, langkah))

    def test_kendaraan_kosong_dan_sampling_gagal_menghasilkan_none(self):
        kapal, kendaraan = baca_data(ROOT / "data/kapal.json", ROOT / "data/kendaraan.json")
        self.assertIsNone(tetangga_acak(kapal, [], {}, random.Random(42)))
        state = inisialisasi_acak(kapal, kendaraan, 42)
        self.assertIsNone(tetangga_acak(kapal, kendaraan, state, random.Random(42), maks_coba=0))

    def test_input_tidak_valid_ditolak(self):
        kapal, kendaraan = baca_data(ROOT / "data/kapal.json", ROOT / "data/kendaraan.json")
        state = inisialisasi_acak(kapal, kendaraan, 42)
        for batas in (-1, True, 1.5):
            with self.subTest(maks_coba=batas), self.assertRaises(ValueError):
                tetangga_acak(kapal, kendaraan, state, random.Random(42), maks_coba=batas)
        with self.assertRaises(ValueError):
            tetangga_acak(kapal, kendaraan, {}, random.Random(42))

    def test_stuck_membedakan_penambahan_rotasi_dan_tukar_satu_langkah(self):
        kapal = [dict(id="k", lebar=2, panjang=1, kapasitas=1)]
        kendaraan = [dict(id="a", lebar=1, panjang=2, berat=1, tarif_kirim=20, eta_hari=3),
                     dict(id="b", lebar=1, panjang=1, berat=1, tarif_kirim=10, eta_hari=0)]
        posisi = dict(kapal_id="k", x=0, y=0, orientasi="horizontal")
        kosong = dict(a=None, b=None)
        self.assertFalse(puncak_lokal(kapal, kendaraan, kosong))
        state = dict(a=None, b=posisi)
        self.assertFalse(puncak_lokal(kapal, kendaraan, state))
        state["b"] = dict(posisi, x=1)
        self.assertTrue(puncak_lokal(kapal, kendaraan, state))
        self.assertEqual(state, dict(a=None, b=dict(posisi, x=1)))

    def test_puncak_lokal_cocok_dengan_seluruh_tetangga_dek_kecil(self):
        kapal = [dict(id="k", lebar=2, panjang=2, kapasitas=3)]
        kendaraan = [dict(id="a", lebar=1, panjang=1, berat=1, tarif_kirim=10, eta_hari=0),
                     dict(id="b", lebar=1, panjang=2, berat=2, tarif_kirim=20, eta_hari=4),
                     dict(id="c", lebar=2, panjang=1, berat=1, tarif_kirim=0, eta_hari=1)]
        pilihan = []
        for data in kendaraan:
            posisi = [None]
            for orientasi in ("vertikal", "horizontal"):
                lebar, panjang = ukuran(data, orientasi)
                for x in range(3 - lebar):
                    for y in range(3 - panjang):
                        posisi.append(dict(kapal_id="k", x=x, y=y, orientasi=orientasi))
            pilihan.append(posisi)
        daftar_id = [k["id"] for k in kendaraan]
        jumlah = 0
        for posisi in product(*pilihan):
            state = dict(zip(daftar_id, posisi))
            try:
                periksa_state(kapal, kendaraan, state)
            except ValueError:
                continue
            semua = []
            for id_kendaraan, posisi_baru in zip(daftar_id, pilihan):
                semua.extend(dict(state, **{id_kendaraan: p}) for p in posisi_baru)
            for a, b in combinations(daftar_id, 2):
                kandidat = dict(state)
                kandidat[a], kandidat[b] = state[b], state[a]
                semua.append(kandidat)
            sebelum = copy.deepcopy(state)
            nilai = nilai_objektif(kapal, kendaraan, state)
            ada_perbaikan = False
            for kandidat in semua:
                try:
                    ada_perbaikan |= nilai_objektif(kapal, kendaraan, kandidat) > nilai
                except ValueError:
                    pass
            self.assertEqual(puncak_lokal(kapal, kendaraan, state), not ada_perbaikan, state)
            self.assertEqual(state, sebelum)
            jumlah += 1
        self.assertGreater(jumlah, 20)


if __name__ == "__main__":
    unittest.main()
