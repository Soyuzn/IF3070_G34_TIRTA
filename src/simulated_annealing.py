"""Adaptasi AIMA edisi 4, bagian 4.1.2, Figure 4.5, hlm. 115 (PDF 128)."""
import math
import random
from copy import deepcopy

from .data import angka_valid, nilai_objektif
from .tetangga import puncak_lokal, tetangga_acak


def probabilitas_penerimaan(delta_e, suhu, evaluation_bias=1):
    """Bias > 1 membuat penurunan nilai lebih sulit diterima; objektif tetap sama."""
    if not angka_valid(suhu) or suhu == 0:
        raise ValueError("suhu harus positif dan berhingga")
    if not angka_valid(evaluation_bias) or evaluation_bias == 0:
        raise ValueError("evaluation_bias harus positif dan berhingga")
    if type(delta_e) not in (int, float) or not math.isfinite(delta_e):
        raise ValueError("delta_e harus angka berhingga")
    return 1.0 if delta_e >= 0 else math.exp((delta_e / suhu) * evaluation_bias)


def _eksponen(delta_e, suhu):
    try:
        nilai = math.exp(delta_e / suhu)
        return nilai if math.isfinite(nilai) else None
    except OverflowError:
        return None


def _jadwal_suhu(iterasi, suhu_awal, pendinginan, suhu_minimum):
    """schedule(t) pada buku; suhu nol menandai akhir pencarian."""
    suhu = suhu_awal * pendinginan ** (iterasi - 1)
    return suhu if suhu >= suhu_minimum else 0


def cari(kapal, kendaraan, state_awal, seed, objektif="tarif_kirim", *,
         suhu_awal=50, pendinginan=.995, suhu_minimum=.1, batas_iterasi=1000,
         evaluation_bias=1, interval_stuck=50, tetangga=tetangga_acak, cek_stuck=puncak_lokal):
    """Kembalikan state terbaik, riwayat state saat ini, dan metrik SA."""
    nilai = nilai_objektif(kapal, kendaraan, state_awal, objektif)
    probabilitas_penerimaan(0, suhu_awal, evaluation_bias)
    if not angka_valid(suhu_minimum) or not 0 < suhu_minimum <= suhu_awal:
        raise ValueError("suhu_minimum harus positif dan tidak melebihi suhu_awal")
    if not angka_valid(pendinginan) or not 0 < pendinginan < 1:
        raise ValueError("pendinginan harus di antara 0 dan 1")
    if type(batas_iterasi) is not int or batas_iterasi < 0:
        raise ValueError("batas_iterasi harus integer nonnegatif")
    if type(interval_stuck) is not int or interval_stuck < 1:
        raise ValueError("interval_stuck harus integer positif")
    if type(seed) is not int:
        raise ValueError("seed harus integer")
    if not callable(tetangga):
        raise ValueError("tetangga harus berupa fungsi")
    if cek_stuck is not None and not callable(cek_stuck):
        raise ValueError("cek_stuck harus fungsi atau None (belum diukur)")
    if not angka_valid(nilai):
        raise ValueError("nilai objektif tidak berhingga")

    acak = random.Random(seed)
    state = deepcopy(state_awal)
    terbaik, nilai_terbaik = deepcopy(state), nilai
    riwayat = [dict(iterasi=0, objektif=nilai)]
    jejak, pemeriksaan = [], []
    diterima = tanpa_kandidat = eksponen_meluap = 0
    alasan = "batas_iterasi"

    for iterasi in range(1, batas_iterasi + 1):
        suhu = _jadwal_suhu(iterasi, suhu_awal, pendinginan, suhu_minimum)
        if suhu == 0:
            alasan = "suhu_minimum"
            break
        hasil = tetangga(kapal, kendaraan, deepcopy(state), acak)
        kandidat, langkah = hasil if hasil is not None else (None, None)
        eksponen = delta_e = peluang = None
        terima = False
        if kandidat is None:
            tanpa_kandidat += 1
        else:
            nilai_baru = nilai_objektif(kapal, kendaraan, kandidat, objektif)
            if not angka_valid(nilai_baru):
                raise ValueError("nilai kandidat tidak berhingga")
            delta_e = nilai_baru - nilai  # Positif berarti shipping fee membaik.
            eksponen = _eksponen(delta_e, suhu)
            eksponen_meluap += eksponen is None
            peluang = probabilitas_penerimaan(delta_e, suhu, evaluation_bias)
            terima = peluang == 1 or acak.random() < peluang
            if terima:
                state, nilai = deepcopy(kandidat), nilai_baru
                diterima += 1
                if nilai > nilai_terbaik:
                    terbaik, nilai_terbaik = deepcopy(state), nilai
        riwayat.append(dict(iterasi=iterasi, objektif=nilai,
                            eksponen_penerimaan=eksponen))
        jejak.append(dict(iterasi=iterasi, suhu=suhu, delta_e=delta_e, langkah=deepcopy(langkah),
                          probabilitas_penerimaan=peluang, diterima=terima))
        if cek_stuck is not None and (iterasi % interval_stuck == 0
                or iterasi == batas_iterasi
                or _jadwal_suhu(iterasi + 1, suhu_awal, pendinginan, suhu_minimum) == 0):
            stuck = cek_stuck(kapal, kendaraan, deepcopy(state), objektif)
            if type(stuck) is not bool:
                raise ValueError("cek_stuck harus mengembalikan bool")
            pemeriksaan.append(dict(iterasi=iterasi, stuck=stuck))

    jumlah_stuck = sum(p["stuck"] for p in pemeriksaan)
    definisi = "Belum diukur."
    if cek_stuck is puncak_lokal:
        definisi = "Tidak ada langkah langsung yang menaikkan objektif; plateau termasuk."
    elif cek_stuck is not None:
        definisi = "Mengikuti pemeriksa yang diberikan."
    metrik = dict(
        parameter_efektif=dict(suhu_awal=suhu_awal, pendinginan=pendinginan,
                              suhu_minimum=suhu_minimum, batas_iterasi=batas_iterasi,
                              evaluation_bias=evaluation_bias, interval_stuck=interval_stuck),
        alasan_berhenti=alasan, jumlah_diterima=diterima, jumlah_tanpa_kandidat=tanpa_kandidat,
        jumlah_eksponen_overflow=eksponen_meluap,
        langkah_sa=jejak, pemeriksaan_stuck=pemeriksaan,
        jumlah_stuck=jumlah_stuck, jumlah_pemeriksaan=len(pemeriksaan),
        frekuensi_stuck=jumlah_stuck / len(pemeriksaan) if pemeriksaan else None,
        satuan_stuck="proporsi pemeriksaan", nilai_terbaik=nilai_terbaik,
        definisi_stuck=definisi,
        generator_tetangga=getattr(tetangga, "__name__", type(tetangga).__name__),
        pemeriksa_stuck=(getattr(cek_stuck, "__name__", type(cek_stuck).__name__)
                         if cek_stuck is not None else None),
    )
    return terbaik, riwayat, metrik
