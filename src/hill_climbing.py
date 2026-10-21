"""Hill-climbing: stochastic, steepest ascent, sideways move, random restart."""
import random

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
        terbaik = max(((sum(tarif[i] for i, p in baru.items() if p), acak.random(), baru)
                       for baru, _ in semua_tetangga(kapal, kendaraan, state)), default=None)
        if terbaik is None or terbaik[0] < nilai:
            break
        if terbaik[0] == nilai:
            if sideways >= maks_sideways:
                break
            sideways += 1
        nilai, state = terbaik[0], terbaik[2]
        baris = {"iterasi": len(riwayat), "objektif": nilai}
        riwayat.append(baris if restart is None else dict(baris, restart=restart))
    return state, sideways


def _random_restart(kapal, kendaraan, state, acak, riwayat, maks_restart):
    """Steepest ascent diulang dari state acak baru; simpan yang terbaik."""
    riwayat[0]["restart"], iterasi_per_restart, terbaik = 0, [], state
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
    return terbaik, iterasi_per_restart


def cari(kapal, kendaraan, state_awal, seed, varian="stochastic", maks_gagal=1000,
         maks_sideways=100, maks_restart=10):
    if varian not in VARIAN:
        raise ValueError(f"varian harus salah satu dari {VARIAN}")
    acak = random.Random(seed)
    riwayat = [{"iterasi": 0, "objektif": nilai_objektif(kapal, kendaraan, state_awal)}]
    if varian == "stochastic":
        akhir = _stochastic(kapal, kendaraan, state_awal, acak, riwayat, maks_gagal)
        return akhir, riwayat, {"varian": varian}
    if varian == "random_restart":
        akhir, per_restart = _random_restart(kapal, kendaraan, state_awal, acak, riwayat,
                                             maks_restart)
        return akhir, riwayat, {"varian": varian, "jumlah_restart": maks_restart,
                                "iterasi_per_restart": per_restart}
    batas = maks_sideways if varian == "sideways" else 0
    akhir, sideways = _steepest(kapal, kendaraan, state_awal, acak, riwayat, batas)
    return akhir, riwayat, {"varian": varian, "jumlah_sideways": sideways}
