from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


def _parse_date(value: Any) -> Optional[datetime]:
    """
    Converte strings de data, objetos datetime ou None em datetime.
    Retorna None se não for possível converter.
    """
    if value in (None, "", "NULL"):
        return None
    if isinstance(value, datetime):
        return value
    value = str(value).strip()
    try:
        # tentativa 1 – formato completo (YYYYMMDDhhmmss)
        return datetime.strptime(value.replace("-", "").replace("T", "").replace(":", ""), "%Y%m%d%H%M%S")
    except ValueError:
        pass
    try:
        # tentativa 2 – apenas YYYYMMDD
        return datetime.strptime(value.replace("-", ''), "%Y%m%d")
    except ValueError:
        return None


def _intervals_overlap(a: Tuple[datetime, datetime], b: Tuple[datetime, datetime]) -> bool:
    """Retorna True se os intervalos [a_ini, a_fim] e [b_ini, b_fim] se sobrepõem."""
    a_ini, a_fim = a
    b_ini, b_fim = b
    return a_ini <= b_fim and b_ini <= a_fim


def _cluster_overlaps(records: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """
    Agrupa registros em clusters cujo intervalo DT_INI–DT_FIN colide.
    Pré-condição: todos os registros têm DT_INI/DT_FIN preenchidos.
    """
    # Ordena pelo início do intervalo
    recs_sorted = sorted(records, key=lambda r: _parse_date(r["DT_INI"]))
    clusters: List[List[Dict[str, Any]]] = []

    for rec in recs_sorted:
        ini = _parse_date(rec["DT_INI"])
        fim = _parse_date(rec["DT_FIN"])
        placed = False
        for cluster in clusters:
            c_ini = _parse_date(cluster[0]["DT_INI"])
            c_fim = max(_parse_date(r["DT_FIN"]) for r in cluster)
            if _intervals_overlap((ini, fim), (c_ini, c_fim)):
                cluster.append(rec)
                placed = True
                break
        if not placed:
            clusters.append([rec])
    return clusters


def txt_auto_select(registros: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Recebe lista de dicionários e devolve a mesma lista com a chave
    'AutoSelection' definida segundo as regras fornecidas.
    """
    # Inicia tudo como False
    for r in registros:
        r["AutoSelection"] = False

    # 1. Agrupamento por Tipo, CNPJ, Competência
    grupos: defaultdict[Tuple[Any, Any, Any], List[Dict[str, Any]]] = defaultdict(list)
    for r in registros:
        chave = (r["Tipo"], r["CNPJ"], r["Competencia"])
        grupos[chave].append(r)

    # Processa cada grupo
    for _, recs in grupos.items():

        # Regra 1 – seleciona o registro com data mais recente entre DT_TRANS e DT_ASSINATURA
        registros_com_data = [
            (r, _parse_date(r.get("DT_ASSINATURA")) or _parse_date(r.get("DT_TRANS")))
            for r in recs
        ]

        # Remove os que não têm nem DT_TRANS nem DT_ASSINATURA
        registros_com_data = [(r, dt) for r, dt in registros_com_data if dt is not None]

        if registros_com_data:
            escolhido, _ = max(registros_com_data, key=lambda tup: tup[1])
            escolhido["AutoSelection"] = True
            continue

        # Regra 2 – nenhuma data → verificar colisão de intervalos
        todos_tem_intervalo = all(_parse_date(r.get("DT_INI")) and _parse_date(r.get("DT_FIN")) for r in recs)
        if not todos_tem_intervalo:
            # Sem intervalos completos para avaliar – nada é selecionado
            continue

        clusters = _cluster_overlaps(recs)
        # dicionários sem colisão => cluster tamanho 1
        for cluster in clusters:
            if len(cluster) == 1:
                cluster[0]["AutoSelection"] = True

        # Regra 3 – resolver clusters com colisão
        for cluster in [c for c in clusters if len(c) > 1]:
            retificadores = [r for r in cluster if str(r.get("Retificador ou Original", "")).lower().startswith("retificador")]
            if retificadores:
                candidatos = retificadores
            else:
                candidatos = cluster  # todos originais
            # maior hashfile (comparação lexicográfica)
            escolhido = max(candidatos, key=lambda r: str(r.get("Hashfile", "")))
            escolhido["AutoSelection"] = True

    return registros


if __name__ == "__main__":
    dados_teste = [
        # GRUPO A – há DT_TRANS → seleciona o mais recente
        {
            "Tipo": "EFD ICMS/IPI", "CNPJ": "11111111000111", "Competencia": "202501",
            "Retificador ou Original": "Original",
            "DT_INI": "2025-01-01", "DT_FIN": "2025-01-31",
            "DT_TRANS": "2025-03-01T08:00:00", "DT_ASSINATURA": None,
            "Hashfile": "HX001",
        },
        {
            "Tipo": "EFD ICMS/IPI", "CNPJ": "11111111000111", "Competencia": "202501",
            "Retificador ou Original": "Retificador",
            "DT_INI": "2025-01-01", "DT_FIN": "2025-01-31",
            "DT_TRANS": "20250225090000", "DT_ASSINATURA": None,
            "Hashfile": "HX002",
        },
        {
            # ← Deve receber AutoSelection = True (DT_TRANS mais recente)
            "Tipo": "EFD ICMS/IPI", "CNPJ": "11111111000111", "Competencia": "202501",
            "Retificador ou Original": "Retificador",
            "DT_INI": "2025-01-01", "DT_FIN": "2025-01-31",
            "DT_TRANS": "20250302080000", "DT_ASSINATURA": None,
            "Hashfile": "HX003",
        },

        # GRUPO B – sem DT_TRANS, mas com DT_ASSINATURA → seleciona o mais recente
        {
            "Tipo": "EFD Pis/Cofins", "CNPJ": "22222222000122", "Competencia": "202402",
            "Retificador ou Original": "Original",
            "DT_INI": "2024-02-01", "DT_FIN": "2024-02-29",
            "DT_TRANS": None, "DT_ASSINATURA": "20240315080000",
            "Hashfile": "HY001",
        },
        {
            # ← Deve receber True
            "Tipo": "EFD Pis/Cofins", "CNPJ": "22222222000122", "Competencia": "202402",
            "Retificador ou Original": "Original",
            "DT_INI": "2024-02-01", "DT_FIN": "2024-02-29",
            "DT_TRANS": None, "DT_ASSINATURA": "20240316080000",
            "Hashfile": "HY002",
        },

        # GRUPO C – sem datas, intervalos NÃO colidem → todos True
        {
            # ← True
            "Tipo": "EFD ICMS/IPI", "CNPJ": "33333333000133", "Competencia": "202401",
            "Retificador ou Original": "Original",
            "DT_INI": "20240101", "DT_FIN": "20240115",
            "DT_TRANS": None, "DT_ASSINATURA": None,
            "Hashfile": "HZ001",
        },
        {
            # ← True
            "Tipo": "EFD ICMS/IPI", "CNPJ": "33333333000133", "Competencia": "202401",
            "Retificador ou Original": "Original",
            "DT_INI": "20240116", "DT_FIN": "20240131",
            "DT_TRANS": None, "DT_ASSINATURA": None,
            "Hashfile": "HZ002",
        },

        # GRUPO D – sem datas, intervalos colidem + há Retificador → pega Retificador com maior hash
        {
            "Tipo": "EFD ICMS/IPI", "CNPJ": "44444444000144", "Competencia": "202401",
            "Retificador ou Original": "Retificador",
            "DT_INI": "20240101", "DT_FIN": "20240115",
            "DT_TRANS": None, "DT_ASSINATURA": None,
            "Hashfile": "RA001",
        },
        {
            # ← True (maior hashfile entre Retificadores)
            "Tipo": "EFD ICMS/IPI", "CNPJ": "44444444000144", "Competencia": "202401",
            "Retificador ou Original": "Retificador",
            "DT_INI": "20240105", "DT_FIN": "20240120",
            "DT_TRANS": None, "DT_ASSINATURA": None,
            "Hashfile": "RB999",
        },
        {
            "Tipo": "EFD ICMS/IPI", "CNPJ": "44444444000144", "Competencia": "202401",
            "Retificador ou Original": "Original",
            "DT_INI": "20240108", "DT_FIN": "20240125",
            "DT_TRANS": None, "DT_ASSINATURA": None,
            "Hashfile": "RA003",
        },

        # GRUPO E – sem datas, intervalos colidem mas só Original → pega Original com maior hash
        {
            "Tipo": "EFD ICMS/IPI", "CNPJ": "55555555000155", "Competencia": "202401",
            "Retificador ou Original": "Original",
            "DT_INI": "20240101", "DT_FIN": "20240120",
            "DT_TRANS": None, "DT_ASSINATURA": None,
            "Hashfile": "OA123",
        },
        {
            # ← True (maior hashfile entre Originais)
            "Tipo": "EFD ICMS/IPI", "CNPJ": "55555555000155", "Competencia": "202401",
            "Retificador ou Original": "Original",
            "DT_INI": "20240105", "DT_FIN": "20240125",
            "DT_TRANS": None, "DT_ASSINATURA": None,
            "Hashfile": "OC999",
        },
        {
            "Tipo": "EFD ICMS/IPI", "CNPJ": "55555555000155", "Competencia": "202401",
            "Retificador ou Original": "Original",
            "DT_INI": "20240110", "DT_FIN": "20240130",
            "DT_TRANS": None, "DT_ASSINATURA": None,
            "Hashfile": "OB456",
        },

        # GRUPO F – dois clusters: um sem colisão (True) + outro com colisão (seleção por Retificador)
        # ➊ Cluster sem colisão
        {
            # ← True (isolado, sem colisão)
            "Tipo": "EFD Contribuições", "CNPJ": "66666666000166", "Competencia": "202501",
            "Retificador ou Original": "Original",
            "DT_INI": "20250101", "DT_FIN": "20250107",
            "DT_TRANS": None, "DT_ASSINATURA": None,
            "Hashfile": "CX001",
        },
        # ➋ Cluster com colisão
        {
            "Tipo": "EFD Contribuições", "CNPJ": "66666666000166", "Competencia": "202501",
            "Retificador ou Original": "Original",
            "DT_INI": "20250108", "DT_FIN": "20250120",
            "DT_TRANS": None, "DT_ASSINATURA": None,
            "Hashfile": "CX002",
        },
        {
            # ← True (Retificador, maior hash do cluster)
            "Tipo": "EFD Contribuições", "CNPJ": "66666666000166", "Competencia": "202501",
            "Retificador ou Original": "Retificador",
            "DT_INI": "20250109", "DT_FIN": "20250121",
            "DT_TRANS": None, "DT_ASSINATURA": None,
            "Hashfile": "CX999",
        },
    ]

    resultado = txt_auto_select(dados_teste)
    for linha in resultado:
        print(linha)
