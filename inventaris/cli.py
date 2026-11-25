"""Antarmuka command line: argparse untuk perintah langsung dan menu interaktif."""

import argparse
import os
import sys

from inventaris import loader, processor, reporter
from inventaris.exceptions import InventarisError
from inventaris.konstanta import BATAS_STOK_MENIPIS, KONDISI_VALID

INPUT_DEFAULT = os.path.join("data", "input", "inventaris.csv")
OUTPUT_DEFAULT = os.path.join("data", "output")


def buat_parser():
    """Bangun parser argumen untuk semua perintah."""
    parser = argparse.ArgumentParser(
        prog="main.py", description="Aplikasi pengolahan data inventaris laboratorium komputer."
    )
    parser.add_argument("-i", "--input", default=INPUT_DEFAULT, help="file input .csv atau .json")
    parser.add_argument("-o", "--output-dir", default=OUTPUT_DEFAULT, help="folder hasil output")
    sub = parser.add_subparsers(dest="perintah", required=True)

    sub.add_parser("tampil", help="tampilkan semua data")
    p_cari = sub.add_parser("cari", help="cari barang berdasarkan nama")
    p_cari.add_argument("kata", help="kata kunci nama barang")
    p_filter = sub.add_parser("filter", help="saring data")
    p_filter.add_argument("--kategori")
    p_filter.add_argument("--kondisi", choices=sorted(KONDISI_VALID))
    p_filter.add_argument("--stok-maks", type=int, help="tampilkan item dengan jumlah <= nilai ini")
    sub.add_parser("rekap", help="rekap nilai aset per kategori + stok menipis")
    sub.add_parser("bersih", help="hapus data duplikat dan simpan hasilnya")
    sub.add_parser("menu", help="jalankan menu interaktif")
    return parser


def ambil_data(path):
    """Muat data dari file, cetak peringatan baris yang dilewati, dan kembalikan list data."""
    data, peringatan = loader.muat_data(path)
    for pesan in peringatan:
        print(f"[PERINGATAN] {pesan}")
    print(f"[INFO] {len(data)} baris valid dimuat dari {path}")
    return data


def jalankan_tampil(data, _args, _out):
    print(reporter.format_tabel(data))


def jalankan_cari(data, args, out):
    hasil = processor.cari_nama(data, args.kata)
    print(reporter.format_tabel(hasil) if hasil else f"Tidak ada barang yang cocok dengan '{args.kata}'.")
    if hasil:
        print("Disimpan ke:", reporter.simpan_csv(hasil, os.path.join(out, "hasil_cari.csv")))


def jalankan_filter(data, args, out):
    hasil = processor.filter_data(data, args.kategori, args.kondisi, args.stok_maks)
    print(reporter.format_tabel(hasil))
    if hasil:
        print("Disimpan ke:", reporter.simpan_csv(hasil, os.path.join(out, "hasil_filter.csv")))


def jalankan_rekap(data, _args, out):
    data, duplikat = processor.hapus_duplikat(data)
    if duplikat:
        print(f"[INFO] {len(duplikat)} baris duplikat diabaikan agar rekap tidak terhitung ganda")
    rekap = processor.rekap_per_kategori(data)
    print(reporter.format_rekap(rekap))
    bermasalah = processor.stok_bermasalah(data)
    print(f"\nStok habis/menipis (jumlah <= {BATAS_STOK_MENIPIS}):")
    for item in bermasalah:
        print(f"  - {item['kode']} {item['nama']}: {item['jumlah']} unit ({processor.status_stok(item['jumlah'])})")
    if not bermasalah:
        print("  (tidak ada)")
    print("Disimpan ke:", reporter.simpan_json(rekap, os.path.join(out, "rekap_kategori.json")))


def jalankan_bersih(data, _args, out):
    unik, duplikat = processor.hapus_duplikat(data)
    print(f"Data awal: {len(data)} | unik: {len(unik)} | duplikat dibuang: {len(duplikat)}")
    for item in duplikat:
        print(f"  - duplikat kode {item['kode']} ({item['nama']})")
    print("Disimpan ke:", reporter.simpan_csv(unik, os.path.join(out, "inventaris_bersih.csv")))


PERINTAH = {
    "tampil": jalankan_tampil,
    "cari": jalankan_cari,
    "filter": jalankan_filter,
    "rekap": jalankan_rekap,
    "bersih": jalankan_bersih,
}


def minta_input(pesan, validator=None):
    """Minta input pengguna berulang sampai valid. Return None jika input ditutup (EOF)."""
    while True:
        try:
            teks = input(pesan).strip()
        except EOFError:
            return None
        if validator is None:
            return teks
        try:
            return validator(teks)
        except ValueError as err:
            print(f"  Input tidak valid: {err}")


def _angka_atau_kosong(teks):
    if teks == "":
        return None
    return int(teks)


def _kondisi_atau_kosong(teks):
    if teks == "":
        return None
    if teks.lower() not in KONDISI_VALID:
        raise ValueError(f"pilih salah satu: {', '.join(sorted(KONDISI_VALID))}")
    return teks.lower()


def _tidak_kosong(teks):
    if not teks:
        raise ValueError("tidak boleh kosong")
    return teks


def jalankan_menu(data, out):
    """Menu interaktif sederhana; berhenti saat memilih 0 atau input ditutup."""
    pilihan_menu = (
        "\n=== MENU INVENTARIS LAB ===\n1. Tampilkan data\n2. Cari nama barang\n"
        "3. Filter data\n4. Rekap per kategori\n5. Hapus duplikat\n0. Keluar"
    )
    while True:
        print(pilihan_menu)
        pilihan = minta_input("Pilih menu: ")
        try:
            if pilihan in (None, "0"):
                print("Sampai jumpa.")
                return
            if pilihan == "1":
                jalankan_tampil(data, None, out)
            elif pilihan == "2":
                kata = minta_input("Kata kunci nama: ", _tidak_kosong)
                if kata is None:
                    return
                jalankan_cari(data, argparse.Namespace(kata=kata), out)
            elif pilihan == "3":
                kat = minta_input("Kategori (kosong = semua): ")
                kond = minta_input("Kondisi baik/rusak/perbaikan (kosong = semua): ", _kondisi_atau_kosong)
                stok = minta_input("Stok maksimal (kosong = bebas): ", _angka_atau_kosong)
                jalankan_filter(data, argparse.Namespace(kategori=kat or None, kondisi=kond, stok_maks=stok), out)
            elif pilihan == "4":
                jalankan_rekap(data, None, out)
            elif pilihan == "5":
                jalankan_bersih(data, None, out)
            else:
                print("Menu tidak dikenal, coba lagi.")
        except InventarisError as err:
            print(f"[ERROR] {err}")


def main(argv=None):
    """Titik masuk program. Return kode keluar (0 sukses, 1 error data, 130 dibatalkan)."""
    args = buat_parser().parse_args(argv)
    try:
        data = ambil_data(args.input)
        if args.perintah == "menu":
            jalankan_menu(data, args.output_dir)
        else:
            PERINTAH[args.perintah](data, args, args.output_dir)
    except InventarisError as err:
        print(f"[ERROR] {err}", file=sys.stderr)
        return 1
    except ValueError as err:
        print(f"[ERROR] {err}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nDibatalkan oleh pengguna.", file=sys.stderr)
        return 130
    return 0
