from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pacote ainda não instalado
    __version__ = "0.0.0.dev0"

from .sped_process.process import generate_individual_reports as sped_txt_parser
from .sped_process.txt_selection import txt_auto_select

__all__ = [ "sped_txt_parser", "txt_auto_select" ]