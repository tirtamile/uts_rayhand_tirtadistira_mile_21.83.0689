# Aplikasi Inventaris Laboratorium Komputer (CLI)

UTS Pemrograman Dasar (TK091) - Universitas AMIKOM Yogyakarta, Semester Ganjil 2026/2027.
Aplikasi command line berbasis Python yang mengolah data inventaris laboratorium: mencari,
menyaring, merekap nilai aset per kategori, membuang data duplikat, dan menyimpan hasilnya
ke CSV/JSON.

## Persyaratan
- Python 3.8 atau lebih baru
- Hanya standard library (csv, json, argparse, os, sys, unittest). Tidak perlu `pip install`.

## Struktur proyek
```
inventaris_lab/
|-- main.py                    # titik masuk program
|-- README.md
|-- inventaris/                # package buatan sendiri
|   |-- __init__.py
|   |-- konstanta.py           # KOLOM, KONDISI_VALID, BATAS_STOK_MENIPIS
|   |-- exceptions.py          # InventarisError, FileDataError, FormatDataError
|   |-- loader.py              # baca + validasi CSV/JSON
|   |-- processor.py           # cari, filter, kelompok, rekap, hapus duplikat
|   |-- reporter.py            # format tabel + simpan CSV/JSON
|   `-- cli.py                 # argparse + menu interaktif
|-- tests/test_inventaris.py   # 16 unit test (unittest)
`-- data/
    |-- input/                 # inventaris.csv, inventaris.json, inventaris_rusak.csv, header_salah.csv
    `-- output/                # hasil program + contoh_eksekusi.txt
```

## Cara menjalankan
Jalankan dari folder `inventaris_lab/`:

```bash
python main.py --help
python main.py tampil                                   # semua data
python main.py cari mouse                               # cari nama barang
python main.py filter --kategori Periferal --kondisi baik
python main.py filter --stok-maks 3                     # stok habis/menipis
python main.py rekap                                    # rekap per kategori -> rekap_kategori.json
python main.py bersih                                   # buang duplikat -> inventaris_bersih.csv
python main.py menu                                     # menu interaktif
python main.py -i data/input/inventaris.json rekap      # input JSON
python main.py -i data/input/inventaris_rusak.csv tampil   # demo penanganan error
python -m unittest -v                                   # jalankan unit test
```
Opsi global: `-i/--input` (default `data/input/inventaris.csv`) dan `-o/--output-dir` (default `data/output`).
Kode keluar: `0` sukses, `1` error data/file, `130` dibatalkan (Ctrl+C).

## Format input
CSV dengan header (urutan kolom bebas, nama kolom harus lengkap):

| kolom | aturan |
|---|---|
| kode | wajib, diubah ke huruf besar, dipakai sebagai kunci duplikat |
| nama, kategori, lokasi | wajib, teks |
| jumlah, harga | bilangan bulat >= 0 |
| kondisi | `baik`, `rusak`, atau `perbaikan` |

JSON: list of object dengan kunci yang sama. Baris yang tidak valid dilewati dan dilaporkan
sebagai `[PERINGATAN]`; program tetap memproses baris lain.

## Format output
- Tabel teks di layar.
- `hasil_cari.csv`, `hasil_filter.csv`, `inventaris_bersih.csv` (kolom sama dengan input).
- `rekap_kategori.json`: `{kategori: {"jenis": n, "unit": n, "nilai": n}}`.

## Alur dependensi antar-module
```
main.py -> inventaris.cli -> loader   -> konstanta, exceptions
                          -> processor -> konstanta
                          -> reporter  -> konstanta, exceptions
```
`cli` satu-satunya module yang berinteraksi dengan pengguna. `processor` murni logika (tanpa I/O),
sehingga mudah diuji. `loader` dan `reporter` menangani file dan menerjemahkan error sistem menjadi
exception aplikasi.

## Penanganan error (defensive programming)
| Kondisi | Perilaku |
|---|---|
| File tidak ada / tidak bisa dibaca | `FileDataError`, pesan jelas, exit code 1 |
| Header kurang, JSON rusak, ekstensi tidak didukung | `FormatDataError`, exit code 1 |
| Baris berisi nilai tidak valid | baris dilewati + peringatan |
| Argumen salah (mis. `--kondisi hilang`) | ditolak argparse dengan pesan penggunaan |
| Input menu salah / kosong / EOF | diminta ulang atau keluar rapi |
| Data kosong | tabel/rekap menampilkan "(tidak ada data)", tidak crash |

## Skenario debugging
Gejala: pada `python main.py rekap` versi awal, kategori Komputer tampil 48 unit (Rp 373.600.000)
padahal total fisik hanya 28 unit. Langkah: (1) bandingkan hasil dengan hitungan manual dari CSV,
(2) jalankan `python main.py bersih` dan temukan 2 kode ganda (`KMP-001`, `MSE-001`),
(3) simpulkan penyebab: rekap menghitung baris duplikat dua kali, (4) perbaiki dengan memanggil
`hapus_duplikat` sebelum rekap, (5) tambahkan test regresi `test_rekap_setelah_dedup_tidak_ganda`.
Setelah perbaikan: Komputer = 28 unit, total aset = Rp 316.555.000.

## Sumber referensi dan bantuan AI
- Dokumentasi Python 3: https://docs.python.org/3/ (modul csv, json, argparse, unittest)
- Bantuan AI: claude ai (membuat codingan)

