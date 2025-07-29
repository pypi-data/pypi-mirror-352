"""
Atalhos de alto nível para o pacote OptTech.
"""
from ..tools import map_files, decompressor, compressor
from ..sped_tools import sped_txt_parser, generate_hash, generate_hash_and_signdate
from ..excel_tools import read_xlsx, write_xlsx


__all__ = [
    "map_files", "decompressor", "compressor", 
    "sped_txt_parser", "generate_hash", "generate_hash_and_signdate",
    "read_xlsx", "write_xlsx"
    ]