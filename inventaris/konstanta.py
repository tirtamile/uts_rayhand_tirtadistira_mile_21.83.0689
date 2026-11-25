"""Konstanta yang dipakai bersama oleh seluruh module."""

KOLOM = ("kode", "nama", "kategori", "jumlah", "harga", "kondisi", "lokasi")
KONDISI_VALID = frozenset({"baik", "rusak", "perbaikan"})
BATAS_STOK_MENIPIS = 3
