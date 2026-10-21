"""Baca data, validasi state, dan buat state awal."""
import json
import math
import random
from pathlib import Path

OBJEKTIF = {
    "tarif_kirim": ("jumlah tarif_kirim", "juta rupiah"),
}


def _tanpa_kunci_ganda(pasangan):
    hasil = dict(pasangan)
    if len(hasil) != len(pasangan):
        raise ValueError("Kunci JSON tidak boleh berulang")
    return hasil


def baca_json(path):
    teks = Path(path).read_text(encoding="utf-8")
    return json.loads(teks, object_pairs_hook=_tanpa_kunci_ganda)


def angka_valid(nilai, minimum=0):
    return type(nilai) in (int, float) and math.isfinite(nilai) and nilai >= minimum


def _periksa_daftar(daftar, kolom, boleh_kosong=True):
    if not isinstance(daftar, list) or (not boleh_kosong and not daftar):
        raise ValueError("Data harus berupa list yang sesuai kontrak")
    id_terpakai = set()
    for data in daftar:
        if not isinstance(data, dict) or set(data) != kolom:
            raise ValueError(f"Atribut data harus tepat: {sorted(kolom)}")
        if not isinstance(data["id"], str) or not data["id"].strip():
            raise ValueError("id harus berupa teks yang tidak kosong")
        if data["id"] in id_terpakai:
            raise ValueError(f"id berulang: {data['id']}")
        id_terpakai.add(data["id"])
        for kunci in kolom - {"id"}:
            nilai = data[kunci]
            if kunci in ("lebar", "panjang", "eta_hari"):
                valid = type(nilai) is int and nilai >= (0 if kunci == "eta_hari" else 1)
            else:
                valid = angka_valid(nilai) and (nilai > 0 or kunci == "tarif_kirim")
            if not valid:
                raise ValueError(f"{kunci} {data['id']} tidak valid")


def periksa_data(kapal, kendaraan):
    _periksa_daftar(kapal, {"id", "lebar", "panjang", "kapasitas"}, boleh_kosong=False)
    if len(kapal) != 1:
        raise ValueError("Skenario harus berisi tepat satu kapal")
    _periksa_daftar(kendaraan, {"id", "lebar", "panjang", "tarif_kirim", "berat", "eta_hari"})


def baca_data(path_kapal="data/kapal.json", path_kendaraan="data/kendaraan.json"):
    kapal, kendaraan = baca_json(path_kapal), baca_json(path_kendaraan)
    periksa_data(kapal, kendaraan)
    return kapal, kendaraan


def ukuran(kendaraan, orientasi):
    if orientasi not in ("vertikal", "horizontal"):
        raise ValueError("orientasi harus vertikal atau horizontal")
    lebar, panjang = kendaraan["lebar"], kendaraan["panjang"]
    return (lebar, panjang) if orientasi == "vertikal" else (panjang, lebar)


def _sel(x, y, lebar, panjang):
    return {(i, j) for i in range(x, x + lebar) for j in range(y, y + panjang)}


def periksa_state(kapal, kendaraan, state):
    """State harus lengkap, di dalam dek, tidak bertabrakan, dan tidak kelebihan berat."""
    periksa_data(kapal, kendaraan)
    if not isinstance(state, dict) or set(state) != {k["id"] for k in kendaraan}:
        raise ValueError("state harus memuat tepat setiap id kendaraan")
    dek = kapal[0]
    terisi, berat = set(), 0

    for data_kendaraan in kendaraan:
        penempatan = state[data_kendaraan["id"]]
        if penempatan is None:
            continue
        kolom = {"kapal_id", "x", "y", "orientasi"}
        if not isinstance(penempatan, dict) or set(penempatan) != kolom:
            raise ValueError(f"Penempatan {data_kendaraan['id']} tidak sesuai kontrak")
        kapal_id = penempatan["kapal_id"]
        if kapal_id != dek["id"]:
            raise ValueError(f"kapal_id tidak dikenal untuk {data_kendaraan['id']}")
        if any(type(penempatan[k]) is not int for k in ("x", "y")):
            raise ValueError(f"Koordinat {data_kendaraan['id']} harus integer")
        lebar, panjang = ukuran(data_kendaraan, penempatan["orientasi"])
        x, y = penempatan["x"], penempatan["y"]
        if x < 0 or y < 0 or x + lebar > dek["lebar"] or y + panjang > dek["panjang"]:
            raise ValueError(f"{data_kendaraan['id']} melewati batas {kapal_id}")
        sel_kendaraan = _sel(x, y, lebar, panjang)
        if not sel_kendaraan.isdisjoint(terisi):
            raise ValueError(f"{data_kendaraan['id']} bertumpang tindih pada {kapal_id}")
        terisi.update(sel_kendaraan)
        berat += data_kendaraan["berat"]
    if berat > dek["kapasitas"]:
        raise ValueError(f"Kapasitas {dek['id']} terlampaui")


def nilai_objektif(kapal, kendaraan, state, objektif="tarif_kirim"):
    """Jumlah tarif kirim kendaraan yang dimuat."""
    if objektif not in OBJEKTIF:
        raise ValueError("objektif yang didukung hanya tarif_kirim")
    periksa_state(kapal, kendaraan, state)
    return sum(k["tarif_kirim"] for k in kendaraan if state[k["id"]] is not None)


def inisialisasi_acak(kapal, kendaraan, seed):
    """Membuat state acak yang valid dan dapat diulang; ini bukan optimasi."""
    periksa_data(kapal, kendaraan)
    if type(seed) is not int:
        raise ValueError("seed harus integer agar percobaan dapat diulang")
    acak = random.Random(seed)
    urutan = list(kendaraan)
    acak.shuffle(urutan)
    state = {k["id"]: None for k in kendaraan}
    dek = kapal[0]
    terisi, berat = set(), 0

    for data_kendaraan in urutan:
        pilihan = [None]
        if berat + data_kendaraan["berat"] <= dek["kapasitas"]:
            for orientasi in ("vertikal", "horizontal"):
                lebar, panjang = ukuran(data_kendaraan, orientasi)
                for x in range(dek["lebar"] - lebar + 1):
                    for y in range(dek["panjang"] - panjang + 1):
                        if _sel(x, y, lebar, panjang).isdisjoint(terisi):
                            pilihan.append({"kapal_id": dek["id"], "x": x, "y": y,
                                            "orientasi": orientasi})
        penempatan = acak.choice(pilihan)
        state[data_kendaraan["id"]] = penempatan
        if penempatan is not None:
            lebar, panjang = ukuran(data_kendaraan, penempatan["orientasi"])
            terisi.update(_sel(penempatan["x"], penempatan["y"], lebar, panjang))
            berat += data_kendaraan["berat"]
    periksa_state(kapal, kendaraan, state)
    return state
