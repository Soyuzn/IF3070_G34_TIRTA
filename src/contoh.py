"""Membuat keluaran ilustrasi tanpa menjalankan algoritma pencarian."""
import argparse

from .data import baca_data, inisialisasi_acak, nilai_objektif
from .pencatatan import simpan_percobaan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kapal", default="data/kapal.json")
    parser.add_argument("--kendaraan", default="data/kendaraan.json")
    parser.add_argument("--output", default="output/ilustrasi")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--tanpa-grafik", action="store_true")
    args = parser.parse_args()

    kapal, kendaraan = baca_data(args.kapal, args.kendaraan)
    state = inisialisasi_acak(kapal, kendaraan, args.seed)
    riwayat = [{"iterasi": 0, "objektif": nilai_objektif(kapal, kendaraan, state)}]
    tujuan = simpan_percobaan(
        args.output, algoritma="ilustrasi_tanpa_pencarian", seed=args.seed,
        parameter={}, kapal=kapal, kendaraan=kendaraan, state_awal=state,
        state_akhir=state, durasi_detik=0, riwayat=riwayat,
        metrik={"catatan": "ILUSTRASI. Tidak ada pencarian; awal sama dengan akhir."},
        ilustrasi=True)
    if not args.tanpa_grafik:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from .visualisasi import gambar_state, gambar_riwayat, gambar_penerimaan

        def simpan(nama, gambar):
            gambar.savefig(tujuan / nama, dpi=150)
            plt.close(gambar)

        simpan("state_awal.png", gambar_state(kapal, kendaraan, state, "ILUSTRASI — awal"))
        simpan("state_akhir.png", gambar_state(kapal, kendaraan, state, "ILUSTRASI — akhir"))
        simpan("objektif.png", gambar_riwayat(riwayat, "ILUSTRASI — hanya iterasi 0"))
        sa = [{"iterasi": 0, "objektif": 0},
              {"iterasi": 1, "objektif": 0, "eksponen_penerimaan": .4},
              {"iterasi": 2, "objektif": 0, "eksponen_penerimaan": 1.2}]
        ga = [{"iterasi": 0, "maksimum_populasi": 10, "rata_rata_populasi": 6},
              {"iterasi": 1, "maksimum_populasi": 12, "rata_rata_populasi": 8}]
        simpan("penerimaan_sa_ilustrasi.png", gambar_penerimaan(sa, "ILUSTRASI — exp(ΔE/T)"))
        simpan("populasi_ga_ilustrasi.png", gambar_riwayat(ga, "ILUSTRASI — statistik populasi"))
    print(f"ILUSTRASI tersimpan: {tujuan}")


if __name__ == "__main__":
    main()
