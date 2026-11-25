"""Exception khusus aplikasi agar penanganan error lebih jelas."""


class InventarisError(Exception):
    """Kelas dasar untuk semua error aplikasi ini."""


class FileDataError(InventarisError):
    """File tidak ditemukan, tidak bisa dibaca, atau tidak bisa ditulis."""


class FormatDataError(InventarisError):
    """Isi file tidak sesuai format yang diharapkan."""
