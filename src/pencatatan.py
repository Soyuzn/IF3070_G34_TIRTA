"""Timer pencarian dan penyimpanan hasil percobaan."""
import csv
import json
from pathlib import Path
from time import perf_counter

from .data import OBJEKTIF, angka_valid, nilai_objektif

KOLOM = ("iterasi", "objektif", "maksimum_populasi", "rata_rata_populasi",
         "eksponen_penerimaan", "restart")


def ukur_pencarian(fungsi, *args, **kwargs):
    """Kembalikan (hasil, durasi_detik) untuk pemanggilan fungsi pencarian saja."""
    mulai = perf_counter()
    hasil = fungsi(*args, **kwargs)
    return hasil, perf_counter() - mulai


def periksa_riwayat(riwayat):
    if not isinstance(riwayat, list) or not riwayat:
        raise ValueError("riwayat harus list yang tidak kosong")
    iterasi_lama = -1
    for baris in riwayat:
        if not isinstance(baris, dict) or set(baris) - set(KOLOM):
            raise ValueError("Kolom riwayat tidak dikenal")
        iterasi = baris.get("iterasi")
        if (type(iterasi) is not int or iterasi <= iterasi_lama
                or (iterasi_lama == -1 and iterasi != 0)):
            raise ValueError("iterasi harus integer meningkat, dimulai dari 0")
        iterasi_lama = iterasi
        maksimum = baris.get("maksimum_populasi")
        rata_rata = baris.get("rata_rata_populasi")
        if (maksimum is None) != (rata_rata is None):
            raise ValueError("Maksimum dan rata-rata populasi harus berpasangan")
        if baris.get("objektif") is None and maksimum is None:
            raise ValueError("Baris harus berisi objektif atau statistik populasi")
        for kolom in KOLOM[1:]:
            nilai = baris.get(kolom)
            if nilai is not None and not angka_valid(nilai):
                raise ValueError(f"{kolom} harus angka berhingga nonnegatif")
        if maksimum is not None and rata_rata > maksimum:
            raise ValueError("Rata-rata populasi melebihi maksimum")
        if baris.get("restart") is not None and type(baris["restart"]) is not int:
            raise ValueError("restart harus integer nonnegatif")


def simpan_percobaan(direktori, *, algoritma, seed, parameter, kapal, kendaraan,
                     state_awal, state_akhir, durasi_detik, riwayat, metrik=None,
                     ilustrasi=False, objektif="tarif_kirim"):
    """Menyimpan hasil.json dan riwayat.csv tanpa menimpa percobaan lama."""
    awal = nilai_objektif(kapal, kendaraan, state_awal, objektif)
    akhir = nilai_objektif(kapal, kendaraan, state_akhir, objektif)
    nama_objektif, satuan_objektif = OBJEKTIF[objektif]
    periksa_riwayat(riwayat)
    if not isinstance(algoritma, str) or not algoritma.strip():
        raise ValueError("algoritma harus diisi")
    if type(seed) is not int or not angka_valid(durasi_detik):
        raise ValueError("seed harus integer; durasi_detik harus valid")
    if not isinstance(parameter, dict) or (metrik is not None and not isinstance(metrik, dict)):
        raise ValueError("parameter dan metrik harus dict")
    if type(ilustrasi) is not bool:
        raise ValueError("ilustrasi harus bool")
    hasil = dict(versi_format=1, ilustrasi=ilustrasi, algoritma=algoritma, seed=seed,
                 parameter=parameter, kapal=kapal, kendaraan=kendaraan,
                 state_awal=state_awal, state_akhir=state_akhir,
                 objektif=nama_objektif, satuan_objektif=satuan_objektif,
                 objektif_awal=awal, objektif_akhir=akhir, durasi_detik=durasi_detik,
                 jumlah_iterasi=riwayat[-1]["iterasi"], riwayat=riwayat,
                 metrik=metrik or {})
    teks_json = json.dumps(hasil, indent=2, ensure_ascii=False, allow_nan=False)
    tujuan = Path(direktori)
    tujuan.mkdir(parents=True, exist_ok=False)
    (tujuan / "hasil.json").write_text(teks_json + "\n", encoding="utf-8")
    with (tujuan / "riwayat.csv").open("w", encoding="utf-8", newline="") as berkas:
        penulis = csv.DictWriter(berkas, fieldnames=KOLOM, lineterminator="\n")
        penulis.writeheader()
        penulis.writerows(riwayat)
    return tujuan
