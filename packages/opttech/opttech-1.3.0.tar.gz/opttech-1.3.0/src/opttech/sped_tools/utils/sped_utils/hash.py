import hashlib
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional
from .signdatetime_extraction import _extract_signing_datetime


def generate_hash_md5( file_path : str ) -> str:
    hash_sha1 = hashlib.md5()
    f_in = open( file=file_path, mode='rb' )
    for chunk in iter( lambda : f_in.read(4096), b"" ):
        hash_sha1.update( chunk )

    f_in.close()
    return hash_sha1.hexdigest().upper()


def generate_hash( file_path : str ) -> str:
    hash_sha1 = hashlib.sha1()
    stop_reg = b"9999|"

    with open(file=file_path, mode='rb') as f_in:
        for line in f_in:
            hash_sha1.update(line)
            try:
                if line[1:6] == stop_reg or line[:5] == stop_reg:
                    hash_sha1.update(b"")
                    break
            except:
                pass


    hash_file = hash_sha1.hexdigest()
    
    # Digito verificador
    hash_list = list(hash_file)
    for i in range(len(hash_list)):
        if hash_list[i].isnumeric():
            hash_list[i] = int(hash_list[i]) * ( 41 - i )
        else:
            hash_list[i] = (ord(hash_list[i]) - 87) * ( 41 - i )
    
    resto = sum( hash_list ) % 11
    if resto < 2:
        digit = 0   
    else:
        digit = 11 - resto

    hash_file += str(digit)

    return hash_file


def generate_hash_and_signdate(file_path: str | Path) -> Tuple[str, datetime]:
    """
    Calcula hashfile + dígito verificador e devolve (hashfile, signing_datetime).
    """
    hash_sha1 = hashlib.sha1()
    stop_reg  = b"9999|"

    assinatura_blob = None
    signdate = None

    with open(file_path, "rb") as f_in:
        for line in f_in:
            hash_sha1.update(line)

            # linha começa com |9999|   ou   9999| (sem pipe inicial)
            if line.startswith(b"|9999|") or line[1:6] == stop_reg:
                assinatura_blob = f_in.read()        # resto do arquivo
                break
        else:
            raise ValueError("Registro |9999| não encontrado – arquivo incompleto.")

        # ----------------------- hashfile + dígito ------------------------------
        hash_file = hash_sha1.hexdigest()
        soma = 0
        for i, ch in enumerate(hash_file):
            val = int(ch, 16) if ch.isdigit() else (ord(ch) - 87)
            soma += val * (41 - i)
        resto = soma % 11
        digit = 0 if resto < 2 else 11 - resto
        hash_file += str(digit)

        # ----------------------- data de assinatura -----------------------------
        if assinatura_blob:
            signdate = _extract_signing_datetime(assinatura_blob.lstrip(b"\r\n"))
            if signdate is not None:
                signdate = signdate.strftime("%Y-%m-%dT%H:%M:%S")

    return hash_file, signdate
