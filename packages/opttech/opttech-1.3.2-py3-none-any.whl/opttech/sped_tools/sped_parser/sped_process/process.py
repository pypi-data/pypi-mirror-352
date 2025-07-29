import os, csv
from tqdm import tqdm
from decimal import Decimal
import shutil
from unidecode import unidecode

from ....tools import map_files, convert_csv2parquet

from ....parameters.constants import *
from ....parameters.sped.constants import *
from ..sped_reports.sped_reports import generate_reports_sped
# from ..sped_reports.consolidate import split_individual_reports
from ..sped_reports.dt_proc import extract_dt_trans_from_log
from .txt_selection import txt_auto_select


def generate_map_file( file_infos : list, output_path : str ) -> bool:
    if len(file_infos) == 0:
        return False

    # MAPA ARQUIVOS
    map_path = os.path.join( output_path, 'mapa_arquivos.csv' )
    f_out = open( map_path, mode='w', newline='', encoding=ENCODING )

    fieldnames = list(file_infos[0])
    fieldnames.remove('REG0000')

    writer = csv.writer(f_out, delimiter=DELIMITER, quotechar=QUOTECHAR, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(fieldnames)

    file_infos.sort( key=lambda x: (x['Tipo'], x['CNPJ'], x['Competencia'], x['Retificador ou Original']), reverse=True )

    for row in file_infos:
        row_to_write = []
        for field in fieldnames:
            row_to_write.append(row[field])
        writer.writerow(row_to_write)
        row_to_write.clear()
    
    f_out.close()

    return True


def generate_map_reports( file_infos : list, output_path : str ) -> bool:
    
    # MAPA REPORTS
    map_path = os.path.join( output_path, 'mapa_reports.csv' )
    f_out = open( map_path, mode='w', newline='', encoding=ENCODING )

    fieldnames = [
        'sped',
        'cnpj',
        'reg',
        'competencia',
        'num_rows',
    ]
    writer = csv.writer(f_out, delimiter=DELIMITER, quotechar=QUOTECHAR, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(fieldnames)

    file_infos.sort(key=lambda x: (x['Tipo'], x['Leiaute'], x['CNPJ'], x['Competencia'], x['Retificador ou Original']), reverse=True)

    for row in file_infos:
        row_to_write = []
        for field in fieldnames:
            row_to_write.append(row[field])
        writer.writerow(row_to_write)
        row_to_write.clear()
    
    f_out.close()

    return True


def write_log( logs : list, output_folder : str ) -> bool:
    fieldnames = []
    for log in logs:
        for field in log:
            if field not in fieldnames:
                fieldnames.append(field)

    log_path = os.path.join(output_folder, 'sped_parser.log')
    f_out = open(log_path, mode='w', newline='', encoding=ENCODING)
    writer = csv.DictWriter(f_out, fieldnames=fieldnames, delimiter=DELIMITER, quotechar=QUOTECHAR, quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    writer.writerows(logs)
    f_out.close()

    return log_path


def generate_individual_reports(
        input_path : str,
        output_path : str = None,
        txt_output_path : str = None,
        preprocessing_folder : str = None,
        files_considered : dict = {},
        map_reports : dict = {},
        processed_speds : dict = {},
        parquet_files : bool = False,
        overwrite : bool = False
    ) -> list:
    
    if input_path == output_path or output_path is None:
        output_path = os.path.join(input_path, 'sped_extractions')
    os.makedirs(output_path, exist_ok=True)

    dt_proc = extract_dt_trans_from_log( input_path )

    logs = []

    list_of_files = map_files( folder_path=input_path, extension='.txt' )
    file_infos = []
    
    result = {
        'files_considered' : files_considered,
        'map_reports' : map_reports,
        'processed_speds' : processed_speds
    }
    for file_path in tqdm( list_of_files, desc='individual_reports' ):
        file_info, local_logs = generate_reports_sped(
            file_path,
            output_path,
            preprocessing_folder = preprocessing_folder,
            files_considered = result['files_considered'],
            map_reports = result['map_reports'],
            dt_proc = dt_proc,
            parquet_files = parquet_files,
            overwrite = overwrite
        )

        # ENRICH LOCAL LOG
        for log_row in local_logs:
            log_row['sped'] = file_info['Tipo']
            log_row['competencia'] = file_info['Competencia']
            log_row['cnpj'] = file_info['CNPJ']
            log_row['file_name'] = os.path.basename(file_path)

        logs.extend(local_logs)
        
        file_infos.append( file_info )
        
        if file_info['Processado'] is True:

            if txt_output_path is not None:
                # if file_info['Hashfile'] not in result['processed_speds']:
                txt_file_name = f"CNPJ_{file_info['CNPJ']}-"
                txt_file_name = f"{txt_file_name}SPED_{file_info['Tipo']}-"
                txt_file_name = f"{txt_file_name}VERSION_{file_info['Leiaute']}-"
                txt_file_name = f"{txt_file_name}COMPETENCIA_{file_info['Competencia'].replace('-','')}-"
                txt_file_name = f"{txt_file_name}RETIFICADOR_{file_info['Retificador ou Original']}-"
                txt_file_name = f"{txt_file_name}DT_TRANS_{file_info['DT_TRANS'].replace('-', '').replace('T', '').replace(':', '')}-"
                txt_file_name = f"{txt_file_name}HASH_{file_info['Hashfile']}.txt"
                txt_file_path = os.path.join( txt_output_path, txt_file_name )
                shutil.copy( file_path, txt_file_path )

            sped = file_info['Tipo']
            hash_file = file_info['Hashfile']
            
            if sped not in result['files_considered']:
                result['files_considered'][sped] = {
                    hash_file : file_info
                }
            else:
                result['files_considered'][sped][hash_file] = file_info

    # # Convert csv to parquet
    # if parquet_files is True:
    #     csv2parquet(folder_path=os.path.join(output_path, 'regs'), overwrite=overwrite)
    #     csv2parquet(folder_path=os.path.join(output_path, 'reports'), overwrite=overwrite)

    file_infos = txt_auto_select(file_infos)
    generate_map_file( file_infos, output_path )

    if list_of_files == []:
        log_message = f'Não foi identificado nenhum arquivo elegível para quebra.'
        log_row = {'function' : 'generate_individual_reports', 'message' : log_message, 'log_type' : 'warning'}
        logs.append( log_row )

    # WRITE LOGS
    log_path = write_log( logs, output_path )

    return result, logs, log_path




def generate_map_xlsx( bot,  output_path : str, con_output_path : str ) -> bool:

    file_reports, map_reports = split_individual_reports( output_path, bot.request['files_considered'] )
    if "XML" in file_reports and len(file_reports) == 1:
        return False

    map_path = os.path.join( output_path, 'SPED_REPORTS', 'mapa_arquivos.csv' )
    if not os.path.exists(map_path):
        return False
    
    f_in = open( map_path, mode='r', newline='', encoding=ENCODING )
    reader = csv.DictReader( f_in, delimiter=DELIMITER, quotechar=QUOTECHAR, escapechar='\\' )
    
    fieldnames = [
        'Tipo',
        'Leiaute',
        'CNPJ',
        'Nome',
        'Competencia',
        'Retificador ou Original',
        'Hashfile',
        'Filename',
        'Processado',
        'DataTransmissao',
        'ArquivoVazio',
        'Mensagem'
    ]

    # Write LIST
    map_list = []
    files_not_processed = []

    row_id = 0
    bot.request['acumulated_file_size'] = Decimal('0')
    for row in reader:
        row_id += 1
        
        sped = row['Tipo']
        
        if row['Processado'] == 'True':
            if sped in bot.request['files_considered']:
                if row['Hashfile'] in bot.request['files_considered'][sped]:
                    row['Processado'] = 'Sim'
                    
                    # PROCESS INFO
                    bot.request['acumulated_file_size'] += Decimal(row['file_size'])
                    if sped not in bot.request['process_info']:
                        bot.request['process_info'][sped] = {
                            'companies' : [row['CNPJ']],
                            'company_qty' : 1,
                            'file_qty' : 1,
                            'file_size' : Decimal(row['file_size']),
                            'line_qty' : Decimal(row['line_qty']),
                            'empty_file' : False if row['empty_file'] in ('False', False) else True if row['empty_file'] in ('True', True) else None,
                            'estimated_elapsed_time' : 0
                        }
                    else:
                        if row['CNPJ'] not in bot.request['process_info'][sped]['companies']:
                            bot.request['process_info'][sped]['companies'].append(row['CNPJ'])
                            bot.request['process_info'][sped]['company_qty'] += 1
                        bot.request['process_info'][sped]['file_qty'] += 1
                        bot.request['process_info'][sped]['file_size'] += Decimal(row['file_size'])
                        bot.request['process_info'][sped]['line_qty'] += Decimal(row['line_qty'])
                    
                else:
                    row['Processado'] = 'Não'
            else:
                row['Processado'] = 'Não'
        else:
            row['Processado'] = 'Não'
        
        row['Mensagem'] = ''
        if row['Repetido'] in ('True', True):
            row['Mensagem'] = f"{row['Mensagem']}Arquivo com Hashfile repetido.\n"

        if row['Termino sem registro 9999'] in ('True', True):
            row['Mensagem'] = f"{row['Mensagem']}Arquivo fora do padrão SPED, terminou sem o registro 9999.\n"
        
        if row['Layout com erro'] in ('True', True):
            row['Mensagem'] = f"{row['Mensagem']}A quantidade de campos de alguns registros não condiz com o layout do arquivo.\n"

        if row['Linha fora do padrao SPED'] in ('True', True):
            row['Mensagem'] = f"{row['Mensagem']}Arquivo com linha(s) fora do padrão SPED.\n"
            
        if row['Estrutura com erro'] in ('True', True):
            row['Mensagem'] = f"{row['Mensagem']}Houve algum erro na estrutura do arquivo.\n"
        
        if row['Mensagem'] != '':
            row['Mensagem'] = row['Mensagem'][:-1]


        if row['Processado'] == 'Não' and row['Tipo'] != '':
            np_row = {
                'Tipo' : row['Tipo'], 
                'CNPJ' : row['CNPJ'], 
                'Relatorio' : '', 
                'Competencia' : row['Competencia'], 
                'DataTransmissao' : row['DT_TRANS'],
                'numero_linhas' : '',
                'Processado' : 'Não - sem dados para processar'
            }
            files_not_processed.append(np_row)

        map_list.append( row )
    f_in.close()
    
    
    # MENSAGEM
    index = 1
    while index < len(map_list):        
        row = map_list[index]
        if row.get('DT_TRANS', '') not in (None, ''):
            index += 1
            continue
        if row['Mensagem'] != '':
            index += 1
            continue
        
        subindex = 1
        while subindex < len(map_list):
            subrow = map_list[subindex]
            if index == subindex:
                subindex += 1
                continue
            
            if row['Tipo'] == subrow['Tipo'] and \
                    row['CNPJ'] == subrow['CNPJ'] and \
                    row['Competencia'] == subrow['Competencia'] and \
                    row['Retificador ou Original'] == 'Retificador' and \
                    subrow['Retificador ou Original'] == 'Retificador' and \
                    row['Competencia'] != subrow['Hashfile']:
                row['Mensagem'] = 'Verificar a última versão do arquivo retificador.'
                break
            
            subindex += 1
        index += 1

    _any_processed = False if len(map_list) > 0 else None
    for row in map_list:
        if row['Processado'] == 'Sim':
            _any_processed = True
            break

    # WRITE CSV MAP_LIST
    csv_map_path = os.path.join(con_output_path, 'Csv', 'mapa_arquivos.csv')
    f_out = open( csv_map_path, mode='w', newline='', encoding=ENCODING )
    writer = csv.DictWriter(f_out, fieldnames=fieldnames, delimiter=DELIMITER, quotechar=QUOTECHAR, quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for row in map_list:
        _row = {}
        for field in fieldnames:
            if field == 'DataTransmissao':
                _row[field] = row['DT_TRANS']
            elif field == 'ArquivoVazio':
                _row[field] = 'Sim' if row['empty_file'] in ('True', True) else 'Não' if row['empty_file'] in ('False', False) else None
            else:
                _row[field] = row[field]
        writer.writerow(_row)

    f_out.close()


    report_fieldnames = [
        'Tipo', 
        'CNPJ', 
        'Relatorio', 
        'Competencia', 
        'numero_linhas', 
        'Hashfile',
        'Processado'
        ]

    # WRITE CSV MAP REPORTS
    csv_report_map_path = os.path.join(con_output_path, 'Csv', 'mapa_relatorios.csv')
    f_out = open( csv_report_map_path, mode='w', newline='', encoding=ENCODING )
    writer = csv.DictWriter(f_out, fieldnames=report_fieldnames, delimiter=DELIMITER, quotechar=QUOTECHAR, quoting=csv.QUOTE_MINIMAL, escapechar='\\')
    writer.writeheader()

    for sped in map_reports:
        for cnpj in map_reports[sped]:
            # SORT COMPETENCIA
            map_reports[sped][cnpj] = dict(sorted(map_reports[sped][cnpj].items(), key=lambda x: x[0]))

            for competencia in map_reports[sped][cnpj]:

                for hashfile in map_reports[sped][cnpj][competencia]:
                    for report in REPORT_REG[sped]:
                        row = {
                            'Tipo' : sped, 
                            'CNPJ' : cnpj, 
                            'Relatorio' : report, 
                            'Competencia' : competencia, 
                            'numero_linhas' : None,
                            'Hashfile' : hashfile,
                            'Processado' : None
                        }

                        if report not in map_reports[sped][cnpj][competencia][hashfile]:
                            row['numero_linhas'] = ''
                            row['Processado'] = 'Não - sem dados para processar'

                        else:
                            num_rows = map_reports[sped][cnpj][competencia][hashfile][report]
                            mensagem = 'Sim' # if value is not None else 'Não - sem dados para processar'

                            row['numero_linhas'] = num_rows
                            row['Processado'] = mensagem

                        writer.writerow(row)

    f_out.close()


    # RESOLVE PROCESS_INFO
    bot.request['acumulated_file_size'] = str(bot.request['acumulated_file_size'])
    for sped in bot.request['process_info']:
        # COMPANY
        bot.request['process_info'][sped]['company_qty'] = str(bot.request['process_info'][sped]['company_qty'])
                
        # FILE SIZE
        bot.request['process_info'][sped]['file_size'] = str(bot.request['process_info'][sped]['file_size'])

        # LINE QTY
        bot.request['process_info'][sped]['line_qty'] = str(bot.request['process_info'][sped]['line_qty'])

        # FILE QTY
        bot.request['process_info'][sped]['file_qty'] = str(bot.request['process_info'][sped]['file_qty'])
    
    return True



def reduce_files_considered( bot ) -> bool:

    for sped in bot.request['files_considered']:
        files_to_consider = {}
        # lista_retificadores_diferentes = []
        # lista_originais_diferentes = []

        internal_eliminated_files = {}
        for hash_file in bot.request['files_considered'][sped]:
            cnpj = bot.request['files_considered'][sped][hash_file]['CNPJ']

            # competencia = bot.request['files_considered'][sped][hash_file]['Competencia']
            dt_ini = bot.request['files_considered'][sped][hash_file]['DT_INI']
            dt_fin = bot.request['files_considered'][sped][hash_file]['DT_FIN']
            dt_trans = bot.request['files_considered'][sped][hash_file]['DT_TRANS']

            ret_ori = bot.request['files_considered'][sped][hash_file]['Retificador ou Original']
            file_info = bot.request['files_considered'][sped][hash_file]

            if cnpj not in internal_eliminated_files:
                internal_eliminated_files[cnpj] = []
            
            if cnpj not in files_to_consider:
                files_to_consider[cnpj] = {
                    'files' : [file_info],
                    'hash_file' : [hash_file]
                }
                
            else:

                # CHECK INTERVAL
                colision = False
                fi_id = 0
                num_fi = len(files_to_consider[cnpj]['files'])
                while fi_id < num_fi:
                    # A data ini e fin do arquivo seguinte não coincide com a do arquivo no files_to_consider
                    if dt_ini > files_to_consider[cnpj]['files'][fi_id]['DT_FIN'] or dt_fin < files_to_consider[cnpj]['files'][fi_id]['DT_INI']:
                       fi_id += 1
                       continue

                    colision = True

                    # O arquivo seguinte tem data de transferência e o corrente não
                    if dt_trans != '' and files_to_consider[cnpj]['files'][fi_id]['DT_TRANS'] == '':
                        # Incluir arquivo seguinte
                        _file_info = files_to_consider[cnpj]['files'].pop(fi_id)
                        internal_eliminated_files[cnpj].append(_file_info)
                        files_to_consider[cnpj]['files'].append(file_info)

                    # A data de transferência do arquivo seguinte é mais recente do que a do arquivo no files_to_consider
                    elif dt_trans != '' and dt_trans > files_to_consider[cnpj]['files'][fi_id]['DT_TRANS']:
                        # Incluir arquivo seguinte
                        _file_info = files_to_consider[cnpj]['files'].pop(fi_id)
                        internal_eliminated_files[cnpj].append(_file_info)
                        files_to_consider[cnpj]['files'].append(file_info)

                    # Arquivos com o mesmo tipo
                    elif ret_ori == files_to_consider[cnpj]['files'][fi_id]['Retificador ou Original']:
                        # Desconsiderar arquivo seguinte
                        internal_eliminated_files[cnpj].append(file_info)
                        internal_eliminated_files[cnpj].append(files_to_consider[cnpj]['files'][fi_id])
                        files_to_consider[cnpj]['files'].pop(fi_id)

                    elif ret_ori == 'Retificador' and files_to_consider[cnpj]['files'][fi_id]['Retificador ou Original'] == 'Original':
                        # Incluir arquivo seguinte
                        _file_info = files_to_consider[cnpj]['files'].pop(fi_id)
                        internal_eliminated_files[cnpj].append(_file_info)
                        files_to_consider[cnpj]['files'].append(file_info)
                    
                    else:
                        # Desconsiderar arquivo seguinte
                        internal_eliminated_files[cnpj].append(file_info)
                    break

                if not colision:
                    files_to_consider[cnpj]['files'].append(file_info)
                    files_to_consider[cnpj]['hash_file'].append(hash_file)

        bot.request['files_considered'][sped].clear()
        for cnpj in files_to_consider:
            for file_info in files_to_consider[cnpj]['files']:
                hash_file = file_info['Hashfile']
                bot.request['files_considered'][sped][hash_file] = file_info
                
    return True
