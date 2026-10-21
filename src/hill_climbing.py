"""Hill-climbing pada state kapal; sementara baru varian stochastic."""
import random

from .data import nilai_objektif
from .tetangga import tetangga_acak


def cari(kapal, kendaraan, state_awal, seed, maks_gagal=1000):
    """Stochastic HC: ambil tetangga acak, terima jika lebih baik.

    Berhenti setelah maks_gagal tetangga berturut-turut tidak memperbaiki.
    """
    acak = random.Random(seed)
    state, nilai = state_awal, nilai_objektif(kapal, kendaraan, state_awal)
    riwayat, gagal = [{"iterasi": 0, "objektif": nilai}], 0
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
    return state, riwayat, {"varian": "stochastic", "maks_gagal": maks_gagal}
