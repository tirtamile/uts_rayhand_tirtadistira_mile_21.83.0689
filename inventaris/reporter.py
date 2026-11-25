"""Format tampilan teks dan penyimpanan hasil ke file CSV/JSON."""

import csv
import json
import os

from inventaris.exceptions import FileDataError
from inventaris.konstanta import KOLOM


def format_rupiah(angka):
    """Format bilangan menjadi 'Rp 1.500.000'."""
    return "Rp " + f"{angka:,}".replace(",", ".")


def format_tabel(data):
    """Ubah list record menjadi tabel teks rata kiri."""
    if not data:
        return "(tidak ada data)"
    lebar = {"kode": 8, "nama": 24, "kategori": 12, "jumlah": 6, "harga": 14, "kondisi": 10, "lokasi": 13}
    baris = [" ".join(k.upper().ljust(lebar[k]) for k in KOLOM)]
    baris.append(" ".join("-" * lebar[k] for k in KOLOM))
    for item in data:
        sel = []
        for k in KOLOM:
            nilai = format_rupiah(item[k]) if k == "harga" else str(item[k])
            sel.append(nilai[: lebar[k]].ljust(lebar[k]))
        baris.append(" ".join(sel))
    baris.append(f"Total: {len(data)} baris")
    return "\n".join(baris)


def format_rekap(rekap):
    """Ubah dict rekap menjadi tabel teks."""
    if not rekap:
        return "(tidak ada data untuk direkap)"
    baris = [f"{'KATEGORI':<14}{'JENIS':>6}{'UNIT':>7}{'NILAI ASET':>20}", "-" * 47]
    for kat, r in rekap.items():
        baris.append(f"{kat:<14}{r['jenis']:>6}{r['unit']:>7}{format_rupiah(r['nilai']):>20}")
    baris.append("-" * 47)
    baris.append(
        f"{'TOTAL':<14}{sum(r['jenis'] for r in rekap.values()):>6}"
        f"{sum(r['unit'] for r in rekap.values()):>7}"
        f"{format_rupiah(sum(r['nilai'] for r in rekap.values())):>20}"
    )
    return "\n".join(baris)


def _siapkan_folder(path):
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)


def simpan_csv(data, path):
    """Simpan list record ke CSV. Return path yang ditulis."""
    try:
        _siapkan_folder(path)
        with open(path, "w", newline="", encoding="utf-8") as f:
            penulis = csv.DictWriter(f, fieldnames=KOLOM)
            penulis.writeheader()
            penulis.writerows(data)
    except OSError as err:
        raise FileDataError(f"gagal menulis file {path}: {err}")
    return path


def simpan_json(objek, path):
    """Simpan objek (list/dict) ke JSON. Return path yang ditulis."""
    try:
        _siapkan_folder(path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(objek, f, indent=2, ensure_ascii=False)
    except OSError as err:
        raise FileDataError(f"gagal menulis file {path}: {err}")
    return path
