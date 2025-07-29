import re
import os
import html
import xml.etree.ElementTree as ET
from ....tools import map_files
from datetime import datetime


def get_dt_trans( hashfile : str, dt_proc : dict, file_name : str ) -> str:
    if hashfile[:-1] in dt_proc:
        return dt_proc[hashfile[:-1]]
    
    if 'SPED-ECD' in file_name:
        # 01423208000186-42102626744-20140101-20141231-G-7678B49D6D1481FDCF9EEEA482F150255BDFE593-1-SPED-ECD.txt
        hashfile_from_filename = file_name.split('-SPED-ECD')[0].split('-')[-2]
        if len(hashfile_from_filename) == 40:
            hashfile_from_filename = hashfile_from_filename.lower()
            if hashfile_from_filename in dt_proc:
                return dt_proc[hashfile_from_filename]

    if 'SPEDECF' in file_name:
        # SPEDECF-03700527000117-20230101-20231231-20240624173524.txt
        dt_trans = file_name.split(".txt")[0].split("-")[-1]
        if len(dt_trans) != 14:
            return ''
        data_obj = None
        try:
            data_obj = datetime.strptime(dt_trans, "%Y%m%d%H%M%S")
        except ValueError:
            return ''
        return data_obj.strftime("%Y-%m-%dT%H:%M:%S")

    if 'PISCOFINS' in file_name:
        # PISCOFINS_20240901_20240930_37549571000190_Original_20241009163508_1998770BE983E31D086C83C1C248D59217B3418D.txt
        name_parts = file_name.split('.txt')[0].split("_")
        hashfile_from_filename = name_parts[-1].lower()
        if len(hashfile_from_filename) == 40:
            if hashfile_from_filename in dt_proc:
                return dt_proc[hashfile_from_filename]
                
            dt_trans = name_parts[-2]
            if len(dt_trans) == 14 and dt_trans.isnumeric():
                data_obj = datetime.strptime(dt_trans, "%Y%m%d%H%M%S")
                return data_obj.strftime("%Y-%m-%dT%H:%M:%S")

    if 'SPED-EFD' in file_name:
        # 01020744000130-9010869746-20141201-20141231-0-4408625200F3A038C592C97E8DFCBD0F7EE6BC71-SPED-EFD.txt
        name_parts = file_name.split('.txt')[0].split("-")
        hashfile_from_filename = name_parts[-3].lower()
        if len(hashfile_from_filename) == 40:
            if hashfile_from_filename in dt_proc:
                return dt_proc[hashfile_from_filename]

    return ''


def search_hash(text : str) -> str:
    # Regex para identificar o hash
    hash_pattern = r'(?:^|[_\-.])([a-f0-9]{40,})(?:[_\-.]|$)'
    # Procurar a primeira ocorrência
    match = re.search(hash_pattern, text.lower())
    # Retornar o hash encontrado ou None
    return match.group(1) if match else None


def extract_dt_trans_from_log(file_folder) -> dict:
    if file_folder is None:
        return {}
    extracted_data = {}

    # INTERNAL FILENAME
    list_of_files = map_files(file_folder, extension='txt', contains="-DT_TRANS_")
    for file_path in list_of_files:
        file_name = os.path.basename(file_path)
        dt_trans = file_name.split('-DT_TRANS_')[-1].split('-')[0].replace('.txt', '')
        if dt_trans == '':
            continue
        hash_value = search_hash(file_name)
        if not hash_value:
            continue
        hash_value = hash_value[:40]
        extracted_data[hash_value] = datetime.strptime(dt_trans, "%Y%m%d%H%M%S").strftime('%Y-%m-%dT%H:%M:%S')

    # LOG    
    list_of_files = map_files(file_folder, extension='log', contains="receitanetbx")    
    for file_path in list_of_files:
        if not os.path.exists(file_path):
            continue

        with open(file_path, 'r', encoding='ISO-8859-1', errors='ignore') as f:
            log_content = f.read()

        # Encontra todas as seções de <message>...</message>
        message_blocks = re.findall(r'<message>(.*?)</message>', log_content, re.DOTALL)

        
        for message in message_blocks:
            # Descodifica entidades HTML para obter o XML real
            message_unescaped = html.unescape(message)

            # Extrai todos os elementos <arquivo>...</arquivo> do message_unescaped
            arquivo_blocks = re.findall(r'(<arquivo.*?>.*?</arquivo>)', message_unescaped, re.DOTALL)
            for arquivo_block in arquivo_blocks:
                try:
                    # Parseia cada <arquivo> individualmente
                    arquivo_xml = ET.fromstring(arquivo_block)
                    hash_value = None
                    data_transmissao = None

                    for atributo in arquivo_xml.findall('atributo'):
                        nome = atributo.get('nome')
                        valor = atributo.get('valor')

                        if 'identificador' in nome.lower() or nome.lower() == 'hash' or nome.lower() == 'recibo':
                            hash_value = valor.lower().split('-')[0]
                        elif 'data rece' in nome.lower() or 'transmiss' in nome.lower() or 'data envio' in nome.lower():
                            data_transmissao = valor

                    if hash_value:
                        extracted_data[hash_value] = data_transmissao


                except ET.ParseError as e:
                    continue

    # REC
    list_of_files = map_files(file_folder, extension='rec')
    for file_path in list_of_files:
        if not os.path.exists(file_path):
            continue

        with open(file_path, 'r', encoding='ISO-8859-1', errors='ignore') as f:
            rec_content = f.read()

            rcp0 = rec_content[:4]
            if rcp0 != 'RCP0':
                continue

            cnpj_d = rec_content[4:19]
            data_transmissao = rec_content[19:33]
            data_transmissao = f"{data_transmissao[4:8]}-{data_transmissao[2:4]}-{data_transmissao[:2]}T{data_transmissao[8:10]}:{data_transmissao[10:12]}:{data_transmissao[12:14]}"

            hash_value = None
            file_name = os.path.basename(file_path)
            if file_name.startswith('PISCOFINS'):
                hash_value = file_name.split('.rec')[0].split('_')[-1].lower()

            # assinatura_digital = rec_content[33:105]
            # hashinterna = rec_content.replace(' ').split(' ')
            # Recibo de entrega

            if hash_value:
                extracted_data[hash_value] = data_transmissao

    return extracted_data



if __name__ == "__main__":
    file_folder = '/home/eduardo/Downloads'  # Substitua pelo caminho do seu arquivo
    encoding = 'utf-8'  # Substitua pela codificação correta do seu arquivo

    dados_extraidos = extract_dt_trans_from_log(file_folder)

    # Exibe os dados extraídos
    for hash_key, reception_date in dados_extraidos.items():
        print(f"Hash: {hash_key}, Data de Recepção: {reception_date}")
