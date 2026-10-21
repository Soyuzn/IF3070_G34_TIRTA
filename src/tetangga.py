"""Tetangga state: pindah, putar, tukar."""
from .data import periksa_state, ukuran

ORIENTASI = ("vertikal", "horizontal")


# shortcut: validasi ulang seluruh state, lambat untuk semua_tetangga; ganti peta sel nanti
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


def _move_acak(kapal, data, state, acak):
    jenis = acak.choice(("pindah", "putar", "tukar"))
    dimuat = [i for i in state if state[i]]
    if jenis == "tukar" and len(state) > 1:
        return ("tukar", *acak.sample(list(state), 2))
    if jenis == "putar" and dimuat:
        return ("putar", acak.choice(dimuat))
    i = acak.choice(list(state))
    keluar = state[i] and acak.random() < .5
    return ("pindah", i, None if keluar else _penempatan_acak(kapal, data[i], acak))


def _terapkan(state, move):
    baru = dict(state)
    if move[0] == "pindah":
        baru[move[1]] = move[2]
    elif move[0] == "putar":
        p = state[move[1]]
        baru[move[1]] = dict(p, orientasi=ORIENTASI[p["orientasi"] == "vertikal"])
    else:
        a, b = move[1:]
        baru[a], baru[b] = state[b], state[a]
    return baru


def tetangga_acak(kapal, kendaraan, state, acak, maks_coba=1000):
    """Return (state_baru, move) valid, atau None jika gagal. State asli tidak diubah."""
    data = {k["id"]: k for k in kendaraan}
    for _ in range(maks_coba):
        move = _move_acak(kapal, data, state, acak)
        baru = _terapkan(state, move)
        if baru != state and _valid(kapal, kendaraan, baru):
            return baru, move
    return None