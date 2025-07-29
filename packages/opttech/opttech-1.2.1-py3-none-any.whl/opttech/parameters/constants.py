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
