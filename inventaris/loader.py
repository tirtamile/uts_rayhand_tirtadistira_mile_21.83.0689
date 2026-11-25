"""Membaca dan memvalidasi data dari file CSV atau JSON."""

import csv
import json
import os

from inventaris.exceptions import FileDataError, FormatDataError
from inventaris.konstanta import KOLOM, KONDISI_VALID


def _ke_int(nilai, nama_kolom):
    """Ubah nilai ke bilangan bulat tidak negatif, atau lempar FormatDataError."""
    try:
        angka = int(str(nilai).strip())
    except ValueError:
        raise FormatDataError(f"kolom '{nama_kolom}' harus bilangan bulat, bukan {nilai!r}")
    if angka < 0:
        raise FormatDataError(f"kolom '{nama_kolom}' tidak boleh negatif ({angka})")
    return angka


def validasi_baris(baris):
    """Validasi satu baris data (dict) dan kembalikan dict yang sudah bersih.

    Parameter:
        baris: dict dengan kunci sesuai KOLOM.
    Return:
        dict dengan jumlah/harga bertipe int dan kode huruf besar.
    Raises:
        FormatDataError: jika ada kolom kosong atau nilai tidak valid.
    """
    kosong = [k for k in KOLOM if baris.get(k) is None or str(baris[k]).strip() == ""]
    if kosong:
        raise FormatDataError(f"kolom kosong: {', '.join(kosong)}")
    bersih = {k: str(baris[k]).strip() for k in KOLOM}
    bersih["kode"] = bersih["kode"].upper()
    bersih["kondisi"] = bersih["kondisi"].lower()
    bersih["jumlah"] = _ke_int(bersih["jumlah"], "jumlah")
    bersih["harga"] = _ke_int(bersih["harga"], "harga")
    if bersih["kondisi"] not in KONDISI_VALID:
        raise FormatDataError(
            f"kondisi {bersih['kondisi']!r} tidak dikenal (pilihan: {', '.join(sorted(KONDISI_VALID))})"
        )
    return bersih


def _proses_baris_mentah(daftar_baris, nomor_awal):
    """Validasi banyak baris; baris yang salah dilewati dan dicatat sebagai peringatan."""
    data, peringatan = [], []
    for nomor, baris in enumerate(daftar_baris, start=nomor_awal):
        if not isinstance(baris, dict):
            peringatan.append(f"Baris {nomor} dilewati: bukan objek/record")
            continue
        try:
            data.append(validasi_baris(baris))
        except FormatDataError as err:
            peringatan.append(f"Baris {nomor} dilewati: {err}")
    return data, peringatan


def baca_csv(path):
    """Baca file CSV. Return (data, peringatan)."""
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            pembaca = csv.DictReader(f)
            kurang = [k for k in KOLOM if k not in (pembaca.fieldnames or [])]
            if kurang:
                raise FormatDataError(f"header CSV kekurangan kolom: {', '.join(kurang)}")
            return _proses_baris_mentah(list(pembaca), nomor_awal=2)
    except FileNotFoundError:
        raise FileDataError(f"file tidak ditemukan: {path}")
    except (PermissionError, IsADirectoryError, UnicodeDecodeError, csv.Error) as err:
        raise FileDataError(f"file tidak bisa dibaca ({path}): {err}")


def baca_json(path):
    """Baca file JSON berisi list of object. Return (data, peringatan)."""
    try:
        with open(path, encoding="utf-8") as f:
            isi = json.load(f)
    except FileNotFoundError:
        raise FileDataError(f"file tidak ditemukan: {path}")
    except json.JSONDecodeError as err:
        raise FormatDataError(f"JSON tidak valid ({path}): {err}")
    except (PermissionError, IsADirectoryError, UnicodeDecodeError) as err:
        raise FileDataError(f"file tidak bisa dibaca ({path}): {err}")
    if not isinstance(isi, list):
        raise FormatDataError("isi JSON harus berupa list of object")
    return _proses_baris_mentah(isi, nomor_awal=1)


def muat_data(path):
    """Pilih pembaca berdasarkan ekstensi file. Return (data, peringatan)."""
    ekstensi = os.path.splitext(path)[1].lower()
    if ekstensi == ".csv":
        return baca_csv(path)
    if ekstensi == ".json":
        return baca_json(path)
    raise FormatDataError(f"ekstensi {ekstensi!r} tidak didukung (gunakan .csv atau .json)")
