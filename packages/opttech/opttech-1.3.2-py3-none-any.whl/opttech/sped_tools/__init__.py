from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pacote ainda não instalado
    __version__ = "0.0.0.dev0"

from .sped_parser import sped_txt_parser, txt_auto_select
from .utils import generate_hash, generate_hash_and_signdate

__all__ = [
    "sped_txt_parser",
    "txt_auto_select"
    "generate_hash",
    "generate_hash_and_signdate"
    ]