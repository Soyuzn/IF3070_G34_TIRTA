"""GA untuk memaksimalkan total tarif kirim pada satu kapal."""
import argparse
import random
from copy import deepcopy
from statistics import mean

from .data import (angka_valid, baca_data, inisialisasi_acak,
                   nilai_objektif, periksa_state, ukuran)
from .pencatatan import simpan_percobaan, ukur_pencarian


def buat_populasi(kapal, kendaraan, state_awal, jumlah_populasi, acak):
    populasi = [deepcopy(state_awal)]
    for _ in range(jumlah_populasi - 1):
        populasi.append(inisialisasi_acak(kapal, kendaraan, acak.getrandbits(64)))
    return populasi


def pilih_induk(populasi, nilai, acak):
    # Semua fitness nol berarti setiap individu punya peluang yang sama.
    return acak.choices(populasi, weights=nilai if any(nilai) else None, k=2)


def perbaiki(kapal, kendaraan, state, acak):
    hasil = {k["id"]: None for k in kendaraan}
    urutan = list(kendaraan)
    acak.shuffle(urutan)
    for k in urutan:
        hasil[k["id"]] = deepcopy(state[k["id"]])
        try:
            periksa_state(kapal, kendaraan, hasil)
        except ValueError:
            hasil[k["id"]] = None
    return hasil


def kawin_silang(kapal, kendaraan, induk_a, induk_b, acak):
    if len(kendaraan) < 2:
        return deepcopy(induk_a), deepcopy(induk_b)
    titik = acak.randrange(1, len(kendaraan))
    anak = []
    for kiri, kanan in ((induk_a, induk_b), (induk_b, induk_a)):
        gabungan = {k["id"]: (kiri if i < titik else kanan)[k["id"]]
                    for i, k in enumerate(kendaraan)}
        anak.append(perbaiki(kapal, kendaraan, gabungan, acak))
    return tuple(anak)


def mutasi(kapal, kendaraan, state, acak, peluang_mutasi):
    hasil = deepcopy(state)
    if not kendaraan or acak.random() >= peluang_mutasi:
        return hasil
    k = acak.choice(kendaraan)
    lama = hasil[k["id"]]
    pilihan = [None]
    dek = kapal[0]
    for orientasi in ("vertikal", "horizontal"):
        lebar, panjang = ukuran(k, orientasi)
        for x in range(dek["lebar"] - lebar + 1):
            for y in range(dek["panjang"] - panjang + 1):
                pilihan.append(dict(kapal_id=dek["id"], x=x, y=y, orientasi=orientasi))
    acak.shuffle(pilihan)
    for posisi in pilihan:
        if posisi == lama:
            continue
        hasil[k["id"]] = posisi
        try:
            periksa_state(kapal, kendaraan, hasil)
            return hasil
        except ValueError:
            continue
    hasil[k["id"]] = lama
    return hasil


def cari(kapal, kendaraan, state_awal, seed,
         jumlah_populasi=20, batas_iterasi=100, peluang_mutasi=0.2):
    if type(seed) is not int:
        raise ValueError("seed harus integer")
    if type(jumlah_populasi) is not int or jumlah_populasi < 2:
        raise ValueError("jumlah_populasi minimal 2")
    if type(batas_iterasi) is not int or batas_iterasi < 0:
        raise ValueError("batas_iterasi harus integer nonnegatif")
    if not angka_valid(peluang_mutasi) or peluang_mutasi > 1:
        raise ValueError("peluang_mutasi harus antara 0 dan 1")
    nilai_objektif(kapal, kendaraan, state_awal)
    acak = random.Random(seed)
    populasi = buat_populasi(kapal, kendaraan, state_awal, jumlah_populasi, acak)
    populasi_awal = deepcopy(populasi)
    riwayat = []

    for iterasi in range(batas_iterasi + 1):
        nilai = [nilai_objektif(kapal, kendaraan, p) for p in populasi]
        terbaik = populasi[nilai.index(max(nilai))]
        riwayat.append(dict(iterasi=iterasi, maksimum_populasi=max(nilai),
                            rata_rata_populasi=mean(nilai)))
        if iterasi == batas_iterasi:
            break
        generasi_baru = [deepcopy(terbaik)]
        while len(generasi_baru) < jumlah_populasi:
            induk_a, induk_b = pilih_induk(populasi, nilai, acak)
            for anak in kawin_silang(kapal, kendaraan, induk_a, induk_b, acak):
                generasi_baru.append(mutasi(kapal, kendaraan, anak, acak, peluang_mutasi))
                if len(generasi_baru) == jumlah_populasi:
                    break
        populasi = generasi_baru

    return deepcopy(terbaik), riwayat, {
        "populasi_awal": populasi_awal, "populasi_akhir": deepcopy(populasi)}


def main():
    from .visualisasi import simpan_gambar

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kapal", default="data/kapal.json")
    parser.add_argument("--kendaraan", default="data/kendaraan.json")
    parser.add_argument("--output", default="output/genetika_42")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--jumlah-populasi", type=int, default=20)
    parser.add_argument("--batas-iterasi", type=int, default=100)
    parser.add_argument("--peluang-mutasi", type=float, default=0.2)
    args = parser.parse_args()
    parameter = dict(jumlah_populasi=args.jumlah_populasi,
                     batas_iterasi=args.batas_iterasi, peluang_mutasi=args.peluang_mutasi)
    kapal, kendaraan = baca_data(args.kapal, args.kendaraan)
    awal = inisialisasi_acak(kapal, kendaraan, args.seed)
    hasil, durasi = ukur_pencarian(
        cari, kapal, kendaraan, awal, args.seed, **parameter)
    akhir, riwayat, metrik = hasil
    awal = max(metrik["populasi_awal"],
               key=lambda p: nilai_objektif(kapal, kendaraan, p))
    tujuan = simpan_percobaan(
        args.output, algoritma="genetic_algorithm", seed=args.seed, parameter=parameter,
        kapal=kapal, kendaraan=kendaraan, state_awal=awal, state_akhir=akhir,
        durasi_detik=durasi, riwayat=riwayat, metrik=metrik)
    simpan_gambar(tujuan)
    print(f"Nilai: {riwayat[0]['maksimum_populasi']:.2f} -> "
          f"{riwayat[-1]['maksimum_populasi']:.2f}; durasi: {durasi:.3f} detik")
    print(f"Hasil tersimpan: {tujuan}")


if __name__ == "__main__":
    main()
