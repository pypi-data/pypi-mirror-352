from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pacote ainda não instalado
    __version__ = "0.0.0.dev0"

from .core import map_files, deep_decompressor, zipper

__all__ = [
    "map_files", 
    "deep_decompressor", "zipper", 
    "__version__"
    ]