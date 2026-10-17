"""Visualisasi state dan riwayat eksperimen."""
import textwrap
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from .data import nilai_objektif, ukuran
from .pencatatan import periksa_riwayat


def gambar_state(kapal, kendaraan, state, judul="Keadaan kapal"):
    objektif = nilai_objektif(kapal, kendaraan, state)
    kendaraan_luar = [k["id"] for k in kendaraan if state[k["id"]] is None]
    catatan = "Di luar kapal: " + (", ".join(kendaraan_luar) or "Tidak ada")
    baris_catatan = textwrap.wrap(catatan, width=100)
    fig, axes = plt.subplots(1, len(kapal), squeeze=False,
                             figsize=(max(7, 6 * len(kapal)), 8))
    warna = {k["id"]: plt.get_cmap("tab20")(i % 20) for i, k in enumerate(kendaraan)}

    for dek, ax in zip(kapal, axes[0]):
        berat = 0
        for data_kendaraan in kendaraan:
            penempatan = state[data_kendaraan["id"]]
            if penempatan is None or penempatan["kapal_id"] != dek["id"]:
                continue
            lebar, panjang = ukuran(data_kendaraan, penempatan["orientasi"])
            x, y = penempatan["x"], penempatan["y"]
            berat += data_kendaraan["berat"]
            ax.add_patch(Rectangle((x, y), lebar, panjang,
                                   facecolor=warna[data_kendaraan["id"]], edgecolor="black", alpha=.85))
            label = f"{data_kendaraan['id']}\n{penempatan['orientasi']}"
            ax.text(x + lebar / 2, y + panjang / 2, label, ha="center", va="center",
                    fontsize=7, rotation=90 if lebar == 1 else 0)
        ax.set(xlim=(0, dek["lebar"]), ylim=(dek["panjang"], 0),
               xlabel="x (sel) →", ylabel="y (sel) ↓",
               title=f"{dek['id']}\nBerat {berat:g}/{dek['kapasitas']:g} unit")
        ax.set_xticks(range(dek["lebar"] + 1))
        ax.set_yticks(range(dek["panjang"] + 1))
        ax.grid(alpha=.25)
        ax.set_aspect("equal")
    fig.suptitle(f"{judul}\nObjektif: {objektif:g} juta rupiah")
    fig.text(.04, .02, "\n".join(baris_catatan), fontsize=9, va="bottom")
    fig.tight_layout(rect=(0, .06 + .026 * len(baris_catatan), 1, .91))
    return fig


def gambar_riwayat(riwayat, judul="Perkembangan objektif"):
    periksa_riwayat(riwayat)
    fig, ax = plt.subplots(figsize=(8, 4))
    seri = (("objektif", "Objektif state saat ini"),
            ("maksimum_populasi", "Maksimum populasi"),
            ("rata_rata_populasi", "Rata-rata populasi"))
    for kolom, label in seri:
        data = [(b["iterasi"], b[kolom]) for b in riwayat if b.get(kolom) is not None]
        if data:
            ax.plot(*zip(*data), label=label, marker="o", markersize=3)
    ax.set(xlabel="Iterasi", ylabel="Tarif kirim (juta rupiah)", title=judul)
    ax.legend()
    ax.grid(alpha=.25)
    fig.tight_layout()
    return fig


def gambar_penerimaan(riwayat, judul="Eksponen penerimaan SA"):
    periksa_riwayat(riwayat)
    data = [(b["iterasi"], b["eksponen_penerimaan"])
            for b in riwayat if b.get("eksponen_penerimaan") is not None]
    if not data:
        raise ValueError("Riwayat tidak memiliki eksponen_penerimaan SA")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(*zip(*data), marker="o", markersize=3)
    ax.set(xlabel="Iterasi", ylabel="exp(ΔE/T)", title=judul)
    ax.grid(alpha=.25)
    fig.tight_layout()
    return fig
