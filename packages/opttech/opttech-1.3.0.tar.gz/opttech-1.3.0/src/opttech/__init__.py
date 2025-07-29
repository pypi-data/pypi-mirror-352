from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pacote ainda não instalado
    __version__ = "0.0.0.dev0"

from .core import map_files, decompressor, compressor, \
    sped_txt_parser, \
    generate_hash, generate_hash_and_signdate, \
    read_xlsx, write_xlsx

__all__ = [
    "map_files", 
    "decompressor", "compressor", 
    "sped_txt_parser",
    "generate_hash", "generate_hash_and_signdate",
    "read_xlsx", "write_xlsx",
    "__version__"
    ]