"""Unit test dengan unittest (standard library). Jalankan: python -m unittest -v"""

import os
import tempfile
import unittest

from inventaris import loader, processor, reporter
from inventaris.exceptions import FileDataError, FormatDataError

DATA = [
    {"kode": "A-1", "nama": "Komputer", "kategori": "Komputer", "jumlah": 2, "harga": 100, "kondisi": "baik", "lokasi": "L1"},
    {"kode": "B-1", "nama": "Mouse Optik", "kategori": "Periferal", "jumlah": 0, "harga": 10, "kondisi": "rusak", "lokasi": "L1"},
    {"kode": "A-1", "nama": "Komputer", "kategori": "Komputer", "jumlah": 2, "harga": 100, "kondisi": "baik", "lokasi": "L1"},
]


class TestProcessor(unittest.TestCase):
    def test_cari_nama_tidak_peka_huruf(self):
        self.assertEqual(len(processor.cari_nama(DATA, "MOUSE")), 1)

    def test_cari_kosong_error(self):
        with self.assertRaises(ValueError):
            processor.cari_nama(DATA, "   ")

    def test_filter_kombinasi(self):
        hasil = processor.filter_data(DATA, kategori="periferal", kondisi="rusak", stok_maks=0)
        self.assertEqual([i["kode"] for i in hasil], ["B-1"])

    def test_rekap_normal(self):
        rekap = processor.rekap_per_kategori(DATA)
        self.assertEqual(rekap["Komputer"], {"jenis": 2, "unit": 4, "nilai": 400})

    def test_rekap_data_kosong(self):
        self.assertEqual(processor.rekap_per_kategori([]), {})

    def test_rekap_setelah_dedup_tidak_ganda(self):
        """Regresi: data duplikat tidak boleh dihitung dua kali pada rekap."""
        unik, _ = processor.hapus_duplikat(DATA)
        self.assertEqual(processor.rekap_per_kategori(unik)["Komputer"]["unit"], 2)

    def test_hapus_duplikat(self):
        unik, dup = processor.hapus_duplikat(DATA)
        self.assertEqual((len(unik), len(dup)), (2, 1))

    def test_status_stok_batas(self):
        self.assertEqual(processor.status_stok(0), "HABIS")
        self.assertEqual(processor.status_stok(3), "MENIPIS")
        self.assertEqual(processor.status_stok(4), "AMAN")
        with self.assertRaises(ValueError):
            processor.status_stok(-1)


class TestLoader(unittest.TestCase):
    def _tulis(self, isi, nama="t.csv"):
        folder = tempfile.mkdtemp()
        path = os.path.join(folder, nama)
        with open(path, "w", encoding="utf-8") as f:
            f.write(isi)
        return path

    def test_file_tidak_ada(self):
        with self.assertRaises(FileDataError):
            loader.muat_data("tidak_ada.csv")

    def test_ekstensi_tidak_didukung(self):
        with self.assertRaises(FormatDataError):
            loader.muat_data("data.xlsx")

    def test_header_kurang(self):
        with self.assertRaises(FormatDataError):
            loader.baca_csv(self._tulis("kode,nama\nA,B\n"))

    def test_baris_buruk_dilewati(self):
        isi = "kode,nama,kategori,jumlah,harga,kondisi,lokasi\nA-1,X,K,1,10,baik,L\nA-2,Y,K,abc,10,baik,L\n"
        data, peringatan = loader.baca_csv(self._tulis(isi))
        self.assertEqual(len(data), 1)
        self.assertEqual(len(peringatan), 1)

    def test_json_tidak_valid(self):
        with self.assertRaises(FormatDataError):
            loader.baca_json(self._tulis("{rusak", "t.json"))


class TestReporter(unittest.TestCase):
    def test_format_rupiah(self):
        self.assertEqual(reporter.format_rupiah(1500000), "Rp 1.500.000")

    def test_tabel_kosong(self):
        self.assertEqual(reporter.format_tabel([]), "(tidak ada data)")

    def test_simpan_dan_baca_kembali(self):
        path = os.path.join(tempfile.mkdtemp(), "sub", "out.csv")
        reporter.simpan_csv(DATA[:2], path)
        data, _ = loader.baca_csv(path)
        self.assertEqual(len(data), 2)


if __name__ == "__main__":
    unittest.main()
