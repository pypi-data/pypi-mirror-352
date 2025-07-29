from types import MappingProxyType

RESERVED_FOLDERS = MappingProxyType({
    'zip_folder' : 'ZIP_FOLDER', 
    'badzip_folder' : 'BADZIP_FOLDER'
})

UNZIP_EXTENSIONS = (
    '.zip',
    '.rar',
    '.7z',
    '.sped',
    '.tar.gz',
    '.tgz'    
)


DELIMITER = '|'
ENCODING = 'UTF-8'
SPED_ENCODING = 'ISO-8859-1'
QUOTECHAR = '"'

EXCEL_WORKBOOK_LIMIT = 500000
EXCEL_SHEET_LIMIT = 500000

CSV_REPORT_FOLDER = 'Csv'
EXCEL_REPORT_FOLDER = 'Excel'
