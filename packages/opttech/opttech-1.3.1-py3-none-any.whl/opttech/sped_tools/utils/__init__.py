from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pacote ainda não instalado
    __version__ = "0.0.0.dev0"

from .sped_utils.hash import generate_hash, generate_hash_and_signdate
from .sped_io import load_sped_dictionary

__all__ = [
    "generate_hash_file",
    "load_sped_dictionary"
    ]