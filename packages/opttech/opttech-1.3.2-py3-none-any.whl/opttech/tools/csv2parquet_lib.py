#!/usr/bin/env python3
"""
csv2parquet_polars.py

Converte todos os .csv de uma pasta (recursivo) para .parquet:

• 1º: Polars streaming (sink_parquet)  ──  baixo uso de RAM, rápido
• 2º: Fallback seguro em lotes com PyArrow ─  nunca estoura memória
"""


from __future__ import annotations

import os
from pathlib import Path
import polars as pl
import pyarrow.csv as pv
import pyarrow.parquet as pq
import pyarrow as pa

from .file_explorer import map_files
# --------------------------------------------------------------------------- #
# 1. POLARS STREAMING (todos os campos como string)                           #
# --------------------------------------------------------------------------- #
def convert_streaming(csv_path: Path, parquet_path: Path, compression: str = "zstd") -> None:
    # Usa open para extrair os nomes das colunas com segurança
    with open(csv_path, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('|')
    schema = {col: pl.Utf8 for col in header}

    lazy = pl.scan_csv(
        csv_path,
        has_header=True,
        separator="|",
        schema=schema,
        infer_schema_length=0,
        null_values=None,
        low_memory=True,
    )

    lazy.sink_parquet(
        parquet_path,
        compression=compression,
        compression_level=3,
    )


# --------------------------------------------------------------------------- #
# 2. PYARROW fallback (todos os campos como string)                           #
# --------------------------------------------------------------------------- #
def convert_batch_arrow(
    csv_path: Path,
    parquet_path: Path,
    batch_rows: int = 1_000_000,
    compression: str = "zstd",
) -> None:
    with open(csv_path, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('|')

    column_types = {col: pa.string() for col in header}

    reader = pv.open_csv(
        csv_path,
        read_options=pv.ReadOptions(block_size=batch_rows * 128),
        parse_options=pv.ParseOptions(delimiter="|"),
        convert_options=pv.ConvertOptions(column_types=column_types)
    )

    batches = list(reader)  # carrega tudo como lista de batches
    table = pa.Table.from_batches(batches)

    pq.write_table(
        table,
        parquet_path,
        compression=compression,
        compression_level=3,
    )


# --------------------------------------------------------------------------- #
# 3. Orquestração por arquivo                                                 #
# --------------------------------------------------------------------------- #
def convert_csv2parquet(csv_path: str | Path, overwrite: bool = False) -> None:
    csv_path = Path(csv_path)
    parquet_path = csv_path.with_suffix(".parquet")

    if parquet_path.exists() and not overwrite:
        return

    try:
        if hasattr(pl.LazyFrame, "sink_parquet"):
            convert_streaming(csv_path, parquet_path)
        else:
            raise AttributeError("sink_parquet indisponível")
    except Exception:
        convert_batch_arrow(csv_path, parquet_path)

    if overwrite is True:
        os.remove(csv_path)
        # print(f"✅ Arquivo convertido: {csv_path} → {parquet_path}")

    return


# --------------------------------------------------------------------------- #
# 4.  Função pública para varrer a pasta                                      #
# --------------------------------------------------------------------------- #
def csv2parquet(folder_path: str | Path, overwrite: bool = False) -> None:
    csv_files = map_files(folder_path=folder_path, extension=".csv")
    for csv_path in csv_files:
        convert_csv2parquet(csv_path, overwrite=overwrite)
