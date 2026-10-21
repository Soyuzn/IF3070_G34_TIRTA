"""Menjalankan eksperimen; hanya fungsi cari yang diukur durasinya."""
import argparse
import csv
import hashlib
import importlib
import json
import platform
from copy import deepcopy
from pathlib import Path
from statistics import mean, stdev

from .data import OBJEKTIF, baca_data, inisialisasi_acak, nilai_objektif
from .pencatatan import simpan_percobaan, ukur_pencarian


def _gambar(tujuan, kapal, kendaraan, awal, akhir, riwayat, objektif, algoritma):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from .visualisasi import gambar_state, gambar_riwayat, gambar_penerimaan

    for tahap, state in (("awal", awal), ("akhir", akhir)):
        gambar = gambar_state(kapal, kendaraan, state, f"{algoritma} - {tahap}", objektif)
        gambar.savefig(tujuan / f"state_{tahap}.png", dpi=150)
        plt.close(gambar)
    gambar = gambar_riwayat(riwayat, f"{algoritma} - perkembangan objektif", objektif)
    gambar.savefig(tujuan / "objektif.png", dpi=150)
    plt.close(gambar)
    if any(b.get("eksponen_penerimaan") is not None for b in riwayat):
        gambar = gambar_penerimaan(riwayat, f"{algoritma} - exp(ΔE/T)")
        gambar.axes[0].set_yscale("symlog", linthresh=1)
        gambar.axes[0].set_ylim(bottom=0)
        gambar.axes[0].axhline(1, color="gray", linestyle="--", linewidth=.8)
        gambar.savefig(tujuan / "penerimaan_sa.png", dpi=150)
        plt.close(gambar)


def _ringkasan(tujuan, hasil, algoritma, objektif):
    with (tujuan / "ringkasan.csv").open("w", encoding="utf-8", newline="") as berkas:
        penulis = csv.DictWriter(berkas, fieldnames=list(hasil[0]))
        penulis.writeheader()
        penulis.writerows(hasil)
    nilai = [h["objektif_akhir"] for h in hasil]
    teks = [f"# Eksperimen {algoritma}", "", f"Objektif: {objektif} ({OBJEKTIF[objektif][1]}).",
            "Hasil pencarian nyata pada dataset sintetis, bukan bukti optimum global.", "",
            "| Ulangan | Seed | OF awal | OF akhir | Iterasi | Durasi (s) | Stuck |",
            "|---|---|---|---|---|---|---|"]
    for h in hasil:
        stuck = "—" if h["frekuensi_stuck"] is None else f"{h['frekuensi_stuck']:.3f}"
        teks.append(f"| {h['ulangan']} | {h['seed']} | {h['objektif_awal']:.3f} | "
                    f"{h['objektif_akhir']:.3f} | {h['jumlah_iterasi']} | "
                    f"{h['durasi_detik']:.6f} | {stuck} |")
    simpangan = f"{stdev(nilai):.3f}" if len(nilai) > 1 else "tidak dihitung (n < 2)"
    teks += ["", f"Rata-rata OF akhir: {mean(nilai):.3f}; simpangan baku sampel: {simpangan}.",
             f"Rata-rata durasi pencarian: {mean(h['durasi_detik'] for h in hasil):.6f} detik.",
             "Stuck mengikuti pemeriksa yang diberikan; — berarti belum diukur.",
             "Parameter, snapshot data, kedua state, dan metrik ada di hasil.json tiap ulangan."]
    (tujuan / "ringkasan.md").write_text("\n".join(teks) + "\n", encoding="utf-8")


def jalankan(cari, kapal, kendaraan, direktori, *, algoritma="sa", daftar_seed=(40, 41, 42),
             parameter=None, objektif="tarif_kirim", grafik=True, siapkan=None):
    """Satu konfigurasi, beberapa ulangan. Hook siapkan dapat menyiapkan populasi GA."""
    if not daftar_seed or any(type(seed) is not int for seed in daftar_seed):
        raise ValueError("daftar_seed harus berisi integer")
    if len(set(daftar_seed)) != len(daftar_seed):
        raise ValueError("seed ulangan tidak boleh berulang")
    parameter = {} if parameter is None else parameter
    if not isinstance(parameter, dict):
        raise ValueError("parameter harus dict")
    if objektif not in OBJEKTIF:
        raise ValueError("objektif yang didukung hanya tarif_kirim")
    tujuan = Path(direktori)
    tujuan.mkdir(parents=True, exist_ok=False)
    semua_hasil = []
    lingkungan = dict(
        python=platform.python_version(), sistem=platform.platform(),
        sha256_src={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sorted(Path(__file__).parent.glob("*.py"))})
    for ulangan, seed in enumerate(daftar_seed, 1):
        argumen = deepcopy(parameter)
        if siapkan is None:
            awal = inisialisasi_acak(kapal, kendaraan, seed)
        else:
            awal, argumen = siapkan(kapal, kendaraan, seed, argumen)
        nilai_awal = nilai_objektif(kapal, kendaraan, awal, objektif)
        hasil, durasi = ukur_pencarian(
            cari, kapal, kendaraan, deepcopy(awal), seed=seed, objektif=objektif, **argumen)
        akhir, riwayat, metrik = hasil
        metrik = dict(metrik, lingkungan=lingkungan)
        argumen = dict(argumen, **metrik.get("parameter_efektif", {}))
        arsip_parameter = {k: getattr(v, "__name__", type(v).__name__) if callable(v) else v
                           for k, v in argumen.items()}
        folder = simpan_percobaan(
            tujuan / f"ulangan_{ulangan}_seed_{seed}", algoritma=algoritma, seed=seed,
            parameter=arsip_parameter, kapal=kapal, kendaraan=kendaraan, state_awal=awal,
            state_akhir=akhir, durasi_detik=durasi, riwayat=riwayat, metrik=metrik,
            objektif=objektif)
        if grafik:
            _gambar(folder, kapal, kendaraan, awal, akhir, riwayat, objektif, algoritma)
        semua_hasil.append(dict(
            ulangan=ulangan, seed=seed, objektif=objektif, objektif_awal=nilai_awal,
            objektif_akhir=nilai_objektif(kapal, kendaraan, akhir, objektif),
            jumlah_iterasi=riwayat[-1]["iterasi"], durasi_detik=durasi,
            frekuensi_stuck=metrik.get("frekuensi_stuck"), direktori=folder.name))
    _ringkasan(tujuan, semua_hasil, algoritma, objektif)
    return semua_hasil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modul", default="src.simulated_annealing")
    parser.add_argument("--kapal", default="data/kapal.json")
    parser.add_argument("--kendaraan", default="data/kendaraan.json")
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, nargs="+", default=[40, 41, 42])
    parser.add_argument("--objektif", choices=OBJEKTIF, default="tarif_kirim")
    parser.add_argument("--parameter", type=json.loads, default={})
    parser.add_argument("--tanpa-grafik", action="store_true")
    args = parser.parse_args()
    modul = importlib.import_module(args.modul)
    kapal, kendaraan = baca_data(args.kapal, args.kendaraan)
    hasil = jalankan(
        modul.cari, kapal, kendaraan, args.output, algoritma=args.modul.rsplit(".", 1)[-1],
        daftar_seed=args.seed, parameter=args.parameter, objektif=args.objektif,
        grafik=not args.tanpa_grafik, siapkan=getattr(modul, "siapkan", None))
    print(f"{len(hasil)} ulangan tersimpan di {args.output}")


if __name__ == "__main__":
    main()
