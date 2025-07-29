from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pacote ainda não instalado
    __version__ = "0.0.0.dev0"

from .core import map_files, decompressor, compressor

__all__ = [
    "map_files", 
    "decompressor", "compressor", 
    "__version__"
    ]