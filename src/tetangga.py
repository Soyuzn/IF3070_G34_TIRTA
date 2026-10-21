"""Tetangga state: pindah, putar, tukar."""
from .data import _sel, nilai_objektif, periksa_state, ukuran

ORIENTASI = ("vertikal", "horizontal")


def _valid(kapal, kendaraan, state):
    try:
        periksa_state(kapal, kendaraan, state)
        return True
    except ValueError:
        return False


def _penempatan_acak(kapal, data, acak):
    dek, orientasi = acak.choice(kapal), acak.choice(ORIENTASI)
    lebar, panjang = ukuran(data, orientasi)
    x = acak.randint(0, max(0, dek["lebar"] - lebar))
    y = acak.randint(0, max(0, dek["panjang"] - panjang))
    return {"kapal_id": dek["id"], "x": x, "y": y, "orientasi": orientasi}


def _langkah_acak(kapal, data, state, acak):
    jenis = acak.choice(("pindah", "putar", "tukar"))
    dimuat = [id_kendaraan for id_kendaraan, posisi in state.items() if posisi is not None]
    if jenis == "tukar" and len(state) > 1:
        return ("tukar", *acak.sample(list(state), 2))
    if jenis == "putar" and dimuat:
        return ("putar", acak.choice(dimuat))
    id_kendaraan = acak.choice(list(state))
    keluar = state[id_kendaraan] is not None and acak.random() < .5
    posisi = None if keluar else _penempatan_acak(kapal, data[id_kendaraan], acak)
    return ("pindah", id_kendaraan, posisi)


def _terapkan(state, langkah):
    baru = {id_kendaraan: dict(posisi) if posisi is not None else None
            for id_kendaraan, posisi in state.items()}
    if langkah[0] == "pindah":
        baru[langkah[1]] = langkah[2]
    elif langkah[0] == "putar":
        posisi = baru[langkah[1]]
        posisi["orientasi"] = "horizontal" if posisi["orientasi"] == "vertikal" else "vertikal"
    else:
        a, b = langkah[1:]
        baru[a], baru[b] = baru[b], baru[a]
    return baru


def tetangga_acak(kapal, kendaraan, state, acak, maks_coba=1000):
    """Hasil: (state_baru, langkah) valid, atau None jika sampling gagal."""
    periksa_state(kapal, kendaraan, state)
    if type(maks_coba) is not int or maks_coba < 0:
        raise ValueError("maks_coba harus integer nonnegatif")
    if not kendaraan:
        return None
    data = {k["id"]: k for k in kendaraan}
    for _ in range(maks_coba):
        langkah = _langkah_acak(kapal, data, state, acak)
        baru = _terapkan(state, langkah)
        if baru != state and _valid(kapal, kendaraan, baru):
            return baru, langkah
    return None


def puncak_lokal(kapal, kendaraan, state):
    """Tidak ada satu langkah valid dengan nilai lebih tinggi; plateau termasuk."""
    nilai = nilai_objektif(kapal, kendaraan, state)
    dimuat = [k for k in kendaraan if state[k["id"]] is not None]
    berat = sum(k["berat"] for k in dimuat)
    dek = kapal[0]

    def membaik(langkah):
        try:
            kandidat = _terapkan(state, langkah)
            return nilai_objektif(kapal, kendaraan, kandidat) > nilai
        except ValueError:
            return False

    for data in kendaraan:
        id_kendaraan = data["id"]
        if state[id_kendaraan] is not None or data["tarif_kirim"] == 0:
            continue
        for muatan in dimuat:
            if membaik(("tukar", id_kendaraan, muatan["id"])):
                return False
        if berat + data["berat"] > dek["kapasitas"]:
            continue
        for orientasi in ORIENTASI:
            lebar, panjang = ukuran(data, orientasi)
            for x in range(dek["lebar"] - lebar + 1):
                for y in range(dek["panjang"] - panjang + 1):
                    posisi = dict(kapal_id=dek["id"], x=x, y=y, orientasi=orientasi)
                    if membaik(("pindah", id_kendaraan, posisi)):
                        return False
    return True



def semua_tetangga(kapal, kendaraan, state):
    """Semua tetangga valid (state_baru, langkah); peta sel dibuat sekali per state."""
    dek, data = kapal[0], {k["id"]: k for k in kendaraan}
    pemilik, berat = {}, 0
    for i, p in state.items():
        if p is not None:
            pemilik.update(dict.fromkeys(_sel(p["x"], p["y"], *ukuran(data[i], p["orientasi"])), i))
            berat += data[i]["berat"]

    def muat(ubah):
        # ubah: {id: posisi_baru}; sel milik kendaraan yang berubah dianggap kosong
        selisih = sum(data[i]["berat"] * ((p is not None) - (state[i] is not None))
                      for i, p in ubah.items())
        if berat + selisih > dek["kapasitas"]:
            return False
        dipakai = set()
        for i, p in ubah.items():
            if p is None:
                continue
            lebar, panjang = ukuran(data[i], p["orientasi"])
            if p["x"] + lebar > dek["lebar"] or p["y"] + panjang > dek["panjang"]:
                return False
            sel = _sel(p["x"], p["y"], lebar, panjang)
            if not dipakai.isdisjoint(sel) or any(pemilik.get(s, i) not in ubah for s in sel):
                return False
            dipakai |= sel
        return True

    posisi = [None] + [{"kapal_id": dek["id"], "x": x, "y": y, "orientasi": o} for o in ORIENTASI
                       for x in range(dek["lebar"]) for y in range(dek["panjang"])]
    calon = []
    for i, p in state.items():
        calon += [(("pindah", i, q), {i: q}) for q in posisi if q != p]
        if p is not None:
            putar = dict(p, orientasi=ORIENTASI[p["orientasi"] == "vertikal"])
            calon.append((("putar", i), {i: putar}))
    ids = list(state)
    calon += [(("tukar", a, b), {a: state[b], b: state[a]})
              for n, a in enumerate(ids) for b in ids[n + 1:] if state[a] != state[b]]
    for langkah, ubah in calon:
        if muat(ubah):
            yield _terapkan(state, langkah), langkah
