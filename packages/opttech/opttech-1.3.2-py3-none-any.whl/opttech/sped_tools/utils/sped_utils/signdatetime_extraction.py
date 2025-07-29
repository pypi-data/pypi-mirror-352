import re
import hashlib
from base64 import b64decode
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple, List

from asn1crypto import cms, tsp, core

# --------------------------------------------------------------------
# utils  ▸ assinatura -------------------------------------------------
# --------------------------------------------------------------------
OID_SIGNINGTIME = "1.2.840.113549.1.9.5"        # já existia
OID_TIMESTAMP   = "1.2.840.113549.1.9.16.2.14"  # RFC-3161

SIGN_TIME_RAW_RE = re.compile(
    rb"\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x09\x05"     # OID 1.2.840.113549.1.9.5
    rb"(?:[\x31\xA0][\x02-\xff]{1,3})*"                 # qualquer comprimento-/SET
    rb"(\x17\x0d\d{12}Z|\x18\x0f\d{14}Z)",               # UTCTime ou GeneralizedTime
    re.DOTALL
)


def _segments(blob: bytes) -> list[bytes]:
    """
    Divide em DERs pelos cabeçalhos SBRCAAEPDR0##### (5 dígitos).
    Pula CR/LF entre blocos.
    """
    segs: list[bytes] = []
    rx = re.compile(rb"SBRCAAEPDR0(\d{5})(?:\r?\n)?")
    pos = 0
    while (m := rx.search(blob, pos)):
        size = int(m.group(1))
        start = m.end()
        end   = start + size
        segs.append(blob[start:end])
        pos = end
        while pos < len(blob) and blob[pos] in (0x0d, 0x0a):
            pos += 1
    if not segs:
        segs.append(blob)          # EFD – só um bloco
    return segs


def _safe_ci(der: bytes) -> cms.ContentInfo | None:
    """
    Decodifica DER/BER → ContentInfo; devolve None em qualquer erro.
    """
    try:
        return cms.ContentInfo.load(der)
    except Exception:
        return None


def _dt_from_cms(ci: cms.ContentInfo) -> datetime | None:
    """
    Extrai primeiro timestamp ou signingTime de um ContentInfo CMS.
    """
    if ci["content_type"].native != "signed_data":
        return None
    sd = ci["content"]
    for signer in sd["signer_infos"]:
        # 1) timestamp RFC-3161
        ua = signer["unsigned_attrs"]
        if ua:
            for attr in ua:
                if attr["type"].dotted == OID_TIMESTAMP:
                    tst_der = attr["values"][0].native
                    tst = tsp.TimeStampToken.load(tst_der)
                    return tst["content"]["tst_info"]["gen_time"].native.replace(
                        tzinfo=timezone.utc
                    )
        # 2) signingTime
        sa = signer["signed_attrs"]
        if sa:
            for attr in sa:
                if attr["type"].dotted == OID_SIGNINGTIME:
                    return attr["values"][0].native.replace(tzinfo=timezone.utc)
    return None


def _dt_from_raw(der: bytes) -> datetime | None:
    m = SIGN_TIME_RAW_RE.search(der)
    if not m:
        return None
    raw = m.group(1)

    if raw.startswith(b"\x17"):            # UTCTime YYMMDDhhmmssZ
        ts12 = raw[2:-1].decode()          # tira 0x17 e 'Z'
        yy = int(ts12[0:2])
        yyyy = 2000 + yy if yy < 70 else 1900 + yy
        ts = f"{yyyy}{ts12[2:]}"           # YYYY + MMDDhhmmss  (14 dígitos)
    else:                                  # GeneralizedTime YYYYMMDDhhmmssZ
        ts = raw[2:-1].decode()            # já está com 14 dígitos

    return datetime.strptime(ts, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)


def _extract_signing_datetime(blob: bytes) -> datetime | None:
    """
    Percorre todos os blocos DER até achar alguma data de assinatura.
    Prioridade: TSA > signingTime > fallback bruto.
    """
    for der in _segments(blob):
        ci = _safe_ci(der)
        if ci:
            dt = _dt_from_cms(ci)
            if dt:
                return dt

        # se não era CMS ou não tinha data → tenta regex bruto
        dt = _dt_from_raw(der)
        if dt:
            return dt
    return None
