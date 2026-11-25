"""Logika pengolahan data: pencarian, filter, pengelompokan, rekap, dan deduplikasi.

Struktur data yang dipakai:
    list  : menyimpan koleksi record berurutan (data inventaris).
    dict  : satu record (kolom -> nilai) dan hasil rekap (kategori -> ringkasan).
    set   : mendeteksi kode duplikat dan daftar kategori unik secara cepat.
"""

from inventaris.konstanta import BATAS_STOK_MENIPIS


def hitung_nilai(item):
    """Nilai aset satu item = jumlah x harga (int)."""
    return item["jumlah"] * item["harga"]


def status_stok(jumlah, batas=BATAS_STOK_MENIPIS):
    """Kembalikan 'HABIS', 'MENIPIS', atau 'AMAN' berdasarkan jumlah stok."""
    if jumlah < 0:
        raise ValueError("jumlah stok tidak boleh negatif")
    if jumlah == 0:
        return "HABIS"
    if jumlah <= batas:
        return "MENIPIS"
    return "AMAN"


def cari_nama(data, kata_kunci):
    """Cari item yang namanya memuat kata kunci (tidak peka huruf besar/kecil)."""
    kata = kata_kunci.strip().lower()
    if not kata:
        raise ValueError("kata kunci pencarian tidak boleh kosong")
    return [item for item in data if kata in item["nama"].lower()]


def filter_data(data, kategori=None, kondisi=None, stok_maks=None):
    """Saring data; kriteria yang bernilai None diabaikan."""
    hasil = []
    for item in data:
        if kategori and item["kategori"].lower() != kategori.strip().lower():
            continue
        if kondisi and item["kondisi"] != kondisi.strip().lower():
            continue
        if stok_maks is not None and item["jumlah"] > stok_maks:
            continue
        hasil.append(item)
    return hasil


def kategori_unik(data):
    """Himpunan (set) kategori yang muncul pada data."""
    return {item["kategori"] for item in data}


def kelompokkan_per_kategori(data):
    """Kelompokkan item ke dict {kategori: [item, ...]}."""
    kelompok = {}
    for item in data:
        kelompok.setdefault(item["kategori"], []).append(item)
    return kelompok


def rekap_per_kategori(data):
    """Rekap tiap kategori: jumlah jenis, total unit, dan total nilai aset.

    Data kosong menghasilkan dict kosong (edge case).
    """
    kelompok = kelompokkan_per_kategori(data)
    return {
        kat: {
            "jenis": len(items),
            "unit": sum(i["jumlah"] for i in items),
            "nilai": sum(hitung_nilai(i) for i in items),
        }
        for kat, items in sorted(kelompok.items())
    }


def total_nilai(data):
    """Total nilai seluruh aset."""
    return sum(hitung_nilai(item) for item in data)


def stok_bermasalah(data, batas=BATAS_STOK_MENIPIS):
    """Item dengan stok habis atau menipis, diurutkan dari stok paling sedikit."""
    return sorted((i for i in data if i["jumlah"] <= batas), key=lambda i: i["jumlah"])


def hapus_duplikat(data):
    """Pisahkan data unik dan duplikat berdasarkan kode barang.

    Return:
        (unik, duplikat): dua list; kemunculan pertama dianggap data asli.
    """
    sudah_ada = set()
    unik, duplikat = [], []
    for item in data:
        if item["kode"] in sudah_ada:
            duplikat.append(item)
        else:
            sudah_ada.add(item["kode"])
            unik.append(item)
    return unik, duplikat
