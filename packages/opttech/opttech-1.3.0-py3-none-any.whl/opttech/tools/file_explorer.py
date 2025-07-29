import os
from ..parameters import RESERVED_FOLDERS

def map_files( 
        folder_path : str, 
        extension : str|list = None, 
        prefix : str = None, 
        sufix : str = None,
        contains : str = None
        )-> list:
    
    if os.path.isfile(folder_path):
        if extension is None:
            return [ folder_path ]
        else:
            if isinstance(extension, str):
                extension = [extension]

            _extension_found = False
            for _ext in extension:
                if folder_path.endswith(_ext) is True:
                    _extension_found = True
                    break
            
            if _extension_found is True:
                return [ folder_path ]
            
        return []

    
    list_of_files = []
    for root, dirs, files in os.walk(folder_path):
        _skip = False
        for resf in RESERVED_FOLDERS.values():
            if resf in root:
                _skip = True

        if _skip == True:
            continue

        for file_name in files:
            if prefix is not None:
                if file_name.startswith(prefix) is False:
                    continue
            
            if sufix is not None:
                if file_name.endswith(sufix) is False:
                    continue

            if contains is not None:
                if contains not in file_name:
                    continue

            if extension is not None:
                if isinstance(extension, str) and not file_name.lower().endswith( extension ):
                    continue
                
                elif isinstance(extension, list):
                    found = False
                    for ext in extension:
                        if file_name.lower().endswith( ext ) is True:
                            found = True
                            break
                    
                    if found == False:
                        continue
            
            file_path = os.path.join(root, file_name)

            if os.path.isfile(file_path) is False:
                continue

            if os.path.exists(file_path) is False:
                continue

            list_of_files.append(file_path)
            
    # SORT
    list_of_files.sort()

    return list_of_files