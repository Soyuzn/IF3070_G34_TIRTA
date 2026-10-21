"""Hill-climbing: stochastic, steepest ascent, sideways move, random restart."""
import random
from copy import deepcopy

from .data import inisialisasi_acak, nilai_objektif
from .tetangga import semua_tetangga, tetangga_acak

VARIAN = ("stochastic", "steepest", "sideways", "random_restart")


def _stochastic(kapal, kendaraan, state, acak, riwayat, maks_gagal):
    nilai, gagal = riwayat[-1]["objektif"], 0
    while gagal < maks_gagal:
        hasil = tetangga_acak(kapal, kendaraan, state, acak)
        if hasil is None:
            break
        nilai_baru = nilai_objektif(kapal, kendaraan, hasil[0])
        if nilai_baru > nilai:
            state, nilai, gagal = hasil[0], nilai_baru, 0
        else:
            gagal += 1
        riwayat.append({"iterasi": len(riwayat), "objektif": nilai})
    return state


def _steepest(kapal, kendaraan, state, acak, riwayat, maks_sideways=0, restart=None):
    """Pindah ke tetangga terbaik; seri diacak. Sideways dihitung total, bukan beruntun."""
    tarif = {k["id"]: k["tarif_kirim"] for k in kendaraan}
    nilai, sideways = riwayat[-1]["objektif"], 0
    while True:
        terbaik = max(((sum(tarif[i] for i, p in baru.items() if p is not None),
                        acak.random(), baru)
                       for baru, _ in semua_tetangga(kapal, kendaraan, state)),
                      key=lambda calon: calon[:2], default=None)
        if terbaik is None or terbaik[0] < nilai:
            break
        if terbaik[0] == nilai:
            if sideways >= maks_sideways:
                break
            sideways += 1
        nilai, state = terbaik[0], terbaik[2]
        baris = {"iterasi": len(riwayat), "objektif": nilai}
        riwayat.append(baris if restart is None else dict(baris, restart=restart))
        if maks_sideways and sideways >= maks_sideways:
            break
    return state, sideways


def cari(kapal, kendaraan, state_awal, seed, maks_gagal=1000, *, varian="stochastic",
         maks_sideways=100, maks_restart=10):
    if type(seed) is not int:
        raise ValueError("seed harus integer")
    for nama, nilai in (("maks_gagal", maks_gagal), ("maks_sideways", maks_sideways),
                        ("maks_restart", maks_restart)):
        if type(nilai) is not int or nilai < 0:
            raise ValueError(f"{nama} harus integer nonnegatif")
    if varian not in VARIAN:
        raise ValueError(f"varian harus salah satu dari {VARIAN}")
    acak = random.Random(seed)
    riwayat = [{"iterasi": 0, "objektif": nilai_objektif(kapal, kendaraan, state_awal)}]
    state = deepcopy(state_awal)
    metrik = dict(varian=varian, parameter_efektif=dict(
        varian=varian, maks_gagal=maks_gagal, maks_sideways=maks_sideways,
        maks_restart=maks_restart))
    if varian == "stochastic":
        akhir = _stochastic(kapal, kendaraan, state, acak, riwayat, maks_gagal)
        return akhir, riwayat, dict(metrik, maks_gagal=maks_gagal)
    if varian != "random_restart":
        batas = maks_sideways if varian == "sideways" else 0
        akhir, sideways = _steepest(kapal, kendaraan, state, acak, riwayat, batas)
        return akhir, riwayat, dict(metrik, jumlah_sideways=sideways)

    riwayat[0]["restart"], iterasi_per_restart = 0, []
    terbaik = state
    for restart in range(maks_restart + 1):
        if restart:
            state = inisialisasi_acak(kapal, kendaraan, acak.randrange(2**31))
            nilai = nilai_objektif(kapal, kendaraan, state)
            riwayat.append({"iterasi": len(riwayat), "objektif": nilai, "restart": restart})
        mulai = len(riwayat)
        state, _ = _steepest(kapal, kendaraan, state, acak, riwayat, restart=restart)
        iterasi_per_restart.append(len(riwayat) - mulai)
        if nilai_objektif(kapal, kendaraan, state) > nilai_objektif(kapal, kendaraan, terbaik):
            terbaik = state
    return terbaik, riwayat, dict(metrik, jumlah_restart=maks_restart,
                                  iterasi_per_restart=iterasi_per_restart)
