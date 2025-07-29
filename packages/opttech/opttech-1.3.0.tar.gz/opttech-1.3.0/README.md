# OptTech Utilities

[![PyPI version](https://badge.fury.io/py/opttech.svg)](https://pypi.org/project/opttech/)


Biblioteca Python desenvolvida e mantida pela **OptTech**.

---

## ⚙️ Instalação

Você pode instalar diretamente via pip:

```bash
# install from PyPI
pip install opttech
```

---

## 🧪 Exemplo de Uso

A seguir, alguns exemplos básicos das principais funções da biblioteca:

### 🔍 map_files — Mapeamento Recursivo de Arquivos

Lista todos os arquivos de uma pasta (incluindo subpastas).

```python
import opttech

file_list = opttech.map_files(folder_path)
```


### 📦 compressor — Compactar Arquivos para ZIP
Compacta um conjunto de arquivos em um único arquivo .zip.

```python
import opttech

opttech.compressor(folder_to_compress)
```

### 🗃️ decompressor — Descompactar Arquivos (zip, rar, 7z, tgz, tar.gz)
Descompacta arquivos comprimidos de uma pasta para uma pasta de destino.

```python
import opttech

opttech.decompressor(folder_path)
```


[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)