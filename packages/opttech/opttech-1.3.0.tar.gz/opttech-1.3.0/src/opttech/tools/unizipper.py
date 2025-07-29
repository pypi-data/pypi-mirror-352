import os
import py7zr
import rarfile
import zipfile
import tarfile
import shutil
import re

from ..parameters import RESERVED_FOLDERS, UNZIP_EXTENSIONS
from .file_explorer import map_files


def file_in_reserved_folder( file_path : str ) -> bool:
    for folder_name in RESERVED_FOLDERS.values():
        if folder_name in file_path:
            return True
    
    return False


def get_extension(
        file_name : str
        ) -> tuple[str, str]:
    file_name_lc = file_name.lower()
    for ext in UNZIP_EXTENSIONS:
        # If the file name ends with the extension (case-insensitive)
        if file_name_lc.endswith(ext):
            return file_name[:-len(ext)], file_name_lc[-len(ext):]
    
    return file_name, ''


def get_compressed_files(
        file_list : str,
        badzip_folder : str
        ) -> list:
    
    compressed_file_list = []
    for file_path in file_list:
        file_path_lc = file_path.lower()
        if  file_in_reserved_folder( file_path ):
            continue
        
        # .zip or .sped
        if file_path_lc.endswith('.zip') or file_path_lc.endswith('.sped'):
            if zipfile.is_zipfile(file_path):
                compressed_file_list.append(file_path)
            else:
                os.makedirs(badzip_folder, exist_ok=True)
                shutil.move( file_path, badzip_folder )

        # .rar
        elif file_path_lc.endswith('.rar'):
            if rarfile.is_rarfile(file_path):
                compressed_file_list.append(file_path)
            else:
                os.makedirs(badzip_folder, exist_ok=True)
                shutil.move( file_path, badzip_folder )
        
        # .7z
        elif file_path_lc.endswith('.7z'):
            if py7zr.is_7zfile(file_path):
                compressed_file_list.append(file_path)
            else:
                os.makedirs(badzip_folder, exist_ok=True)
                shutil.move( file_path, badzip_folder )
            
        # .tar.gz or .tgz
        elif file_path_lc.endswith('.tar.gz') or file_path_lc.endswith('.tgz'):
            if tarfile.is_tarfile(file_path):
                compressed_file_list.append(file_path)
            else:
                os.makedirs(badzip_folder, exist_ok=True)
                shutil.move(file_path, badzip_folder)

    return compressed_file_list


def get_allowed_files(
        name_list : list,
        allowed_extension : str = None
        ) -> list:
    
    if allowed_extension is None:
        return name_list

    _name_list = []
    for file_name in name_list:
        if file_name.endswith(allowed_extension) or any(file_name.endswith(ext) for ext in UNZIP_EXTENSIONS):
            _name_list.append(file_name)

    return _name_list
    

def decompress_files( 
        list_of_files : list, 
        comp_file_folder : str, 
        badzip_folder : str, 
        allowed_extension : str = None, 
        level : int = 1 
        ) -> list:
    
    file_list = []
    for compressed_file_path in list_of_files:
        aux_compressed_file_path, extension = get_extension( compressed_file_path )
        output_folder = f'{aux_compressed_file_path}_{extension[1:].replace(".", "_")}'
        os.makedirs(  output_folder, exist_ok=True )

        bad_zip = False

        # ZIP
        _file_list = []
        if extension == '.zip':
            try:
                with zipfile.ZipFile( file=compressed_file_path, mode='r' ) as archive:
                    _name_list = get_allowed_files( archive.namelist(), allowed_extension )
                    archive.extractall(output_folder, members=_name_list )

                    for file_name in _name_list:
                        file_path = os.path.join(output_folder, os.path.normpath(file_name))
                        _file_list.append(file_path)

            except Exception as e:
                common_prefix = os.path.commonprefix([compressed_file_path, badzip_folder])
                bad_zip_path = os.path.join(badzip_folder, compressed_file_path.replace(os.path.dirname(common_prefix), '')[1:])
                os.makedirs(bad_zip_path, exist_ok=True)
                shutil.move( compressed_file_path, bad_zip_path )
                bad_zip = True

        # SPED
        elif extension == '.sped':
            try:
                with zipfile.ZipFile( file=compressed_file_path, mode='r' ) as archive:
                    _name_list = get_allowed_files( archive.namelist(), allowed_extension )
                    archive.extractall(output_folder, members=_name_list )

                    for file_name in _name_list:
                        file_path = os.path.join(output_folder, os.path.normpath(file_name))

                        _, file_extension = os.path.splitext(file_path)

                        # RENAME FILE TO INSERT .txt
                        if file_extension == '':
                            os.rename(file_path, f'{file_path}.txt')
                            file_path = f'{file_path}.txt'

                        _file_list.append(file_path)

            except Exception as e:
                common_prefix = os.path.commonprefix([compressed_file_path, badzip_folder])
                bad_zip_path = os.path.join(badzip_folder, compressed_file_path.replace(os.path.dirname(common_prefix), '')[1:])
                os.makedirs(bad_zip_path, exist_ok=True)
                shutil.move( compressed_file_path, bad_zip_path )
                bad_zip = True


        # RAR
        elif extension == '.rar':
            try:
                with rarfile.RarFile( file=compressed_file_path, mode='r' ) as archive:
                    _name_list = get_allowed_files( archive.namelist(), allowed_extension )
                    archive.extractall( output_folder, members=_name_list )

                    for file_name in _name_list:
                        file_path = os.path.join(output_folder, os.path.normpath(file_name))
                        _file_list.append(file_path)

            except Exception as e:
                common_prefix = os.path.commonprefix([compressed_file_path, badzip_folder])
                bad_zip_path = os.path.join(badzip_folder, compressed_file_path.replace(os.path.dirname(common_prefix), '')[1:])
                os.makedirs(bad_zip_path, exist_ok=True)
                shutil.move( compressed_file_path, bad_zip_path )
                bad_zip = True

        # 7Z
        elif extension == '.7z':
            try:
                with py7zr.SevenZipFile( file=compressed_file_path, mode='r' ) as archive:
                    _name_list = get_allowed_files( archive.getnames(), allowed_extension )
                    archive.extract(output_folder, targets=_name_list )

                    for file_name in _name_list:
                        file_path = os.path.join(output_folder, os.path.normpath(file_name))
                        _file_list.append(file_path)

            except Exception as e:
                common_prefix = os.path.commonprefix([compressed_file_path, badzip_folder])
                bad_zip_path = os.path.join(badzip_folder, compressed_file_path.replace(os.path.dirname(common_prefix), '')[1:])
                os.makedirs(bad_zip_path, exist_ok=True)
                shutil.move( compressed_file_path, bad_zip_path )
                bad_zip = True

        # TAR.GZ or TGZ
        elif extension == '.tar.gz' or extension == '.tgz':
            try:
                with tarfile.open( compressed_file_path, 'r:gz' ) as archive:
                    _name_list = get_allowed_files( archive.getnames(), allowed_extension )
                    archive.extractall( path=output_folder, members=(member for member in archive if member.name in _name_list) )

                    for file_name in _name_list:
                        file_path = os.path.join(output_folder, os.path.normpath(file_name))
                        _file_list.append(file_path)

            except Exception as e:
                common_prefix = os.path.commonprefix([compressed_file_path, badzip_folder])
                bad_zip_path = os.path.join(badzip_folder, compressed_file_path.replace(os.path.dirname(common_prefix), '')[1:])
                os.makedirs(bad_zip_path, exist_ok=True)
                shutil.move( compressed_file_path, bad_zip_path )
                bad_zip = True
            
        file_list += get_compressed_files( _file_list, badzip_folder )
        
        if bad_zip:
            continue

        if level == 1:
            shutil.move( compressed_file_path, comp_file_folder )
        else:
            os.remove(compressed_file_path)

    return file_list


def decompressor( 
        folder_path : str, 
        allowed_extension : str = None 
        ) -> bool:
    
    if not os.path.exists(folder_path):
        return False

    file_list = map_files( folder_path, UNZIP_EXTENSIONS )
    if file_list == []:
        return None
    
    badzip_folder = os.path.join( folder_path, RESERVED_FOLDERS['badzip_folder'] )
    file_list = get_compressed_files( file_list, badzip_folder )
    if file_list == []:
        return None
    
    zip_folder = os.path.join( folder_path, RESERVED_FOLDERS['zip_folder'] )
    os.makedirs(zip_folder, exist_ok=True)

    level = 1
    while file_list != []:
        file_list = decompress_files( file_list, zip_folder, badzip_folder, allowed_extension, level )
        print(f'level {level} decompression done, files found:', len(file_list))
        level += 1

    return True


def split_files( 
        split_by_fields : list, 
        folder_to_compress : str, 
        extension 
        ) -> list:
    
    file_paths = {}
    file_list = None
    if isinstance( folder_to_compress, str ):
        file_list = map_files( folder_to_compress, extension = extension )
    elif isinstance( folder_to_compress, list ):
        file_list = folder_to_compress
    else:
        raise ValueError('ERROR: [uni_zipper, split_files] folder_to_compress type error')

    if split_by_fields == []:
        file_paths[''] = file_list
        return file_paths

    for file_path in file_list:
        file_name = os.path.basename(file_path)

        key = ''
        for field in split_by_fields:
            _match = re.search( fr"\s{field}-(.*)[\s.]", file_name )
            if _match:
                value = _match.group(1)
                key = f"{key}{value}|"
        
        if key not in file_paths:
            file_paths[key] = []
        file_paths[key].append(file_path)
        
    return file_paths


def zipper_files(
        file_list : list,
        zip_name : str,
        zip_folder : str
        ) -> str|bool:

    os.makedirs( zip_folder, exist_ok=True )

    common_prefix = None
    if len(file_list) != 1:
        common_prefix = f'{os.path.commonpath(file_list)}/'
    else:
        common_prefix = os.path.dirname(file_list[0])
    
    if not zip_name.endswith('.zip'):
        zip_name = f'{zip_name}.zip'
    zip_file_path = os.path.join( zip_folder, zip_name )

    with zipfile.ZipFile(file=zip_file_path, mode='w', compression=zipfile.ZIP_DEFLATED) as zipf:
        for file_path in file_list:
            zipf.write(file_path, arcname=file_path.replace(common_prefix, ''))

    return zip_file_path


def compressor( 
        folder_to_compress : str, 
        zip_folder : str = None,
        zip_name : str = None, 
        extension : str = None,
        split_by_fields : list = []
        ) -> list:
    if zip_folder is None:
        zip_folder = folder_to_compress
    
    file_lists = split_files( split_by_fields, folder_to_compress, extension )
    for key in file_lists:
        file_lists[key] = [file_path for file_path in file_lists[key] if file_path.endswith('.pickle') is False]

    zip_paths = []
    aux_zip_name = None
    for file_key, file_list in file_lists.items():
        if file_list == []:
            continue
        keys = {field : value for field, value in zip(split_by_fields, file_key.split('|')[:-1])}

        sufix_name = '_'.join( [ f'{field}-{value}' for field, value in keys.items() ] )

        if isinstance(folder_to_compress, str):
            if zip_name is None:
                aux_zip_name = os.path.basename(folder_to_compress) if sufix_name == '' else f'{os.path.basename(folder_to_compress)}_{sufix_name}'
            else:
                aux_zip_name = zip_name if sufix_name == '' else f'{zip_name}_{sufix_name}'
        else:
            common_path = os.path.commonpath(file_list)
            if os.path.isdir(common_path) == False:
                common_path = os.path.dirname(common_path)

            if zip_name is None:
                common_path = os.path.commonpath(file_list)
                aux_zip_name = os.path.basename(common_path) if sufix_name == '' else f'{os.path.basename(common_path)}_{sufix_name}'
            else:
                aux_zip_name = zip_name if sufix_name == '' else f'{zip_name}_{sufix_name}'

        zip_path = zipper_files( 
            file_list = file_list,
            zip_name = aux_zip_name,
            zip_folder = zip_folder
        )
        zip_paths.append(zip_path)

    return zip_paths
