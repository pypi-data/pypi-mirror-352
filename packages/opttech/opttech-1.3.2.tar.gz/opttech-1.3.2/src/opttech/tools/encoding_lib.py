from charset_normalizer import from_bytes


def detect_charset(chunk: bytes) -> dict:
    result = from_bytes(chunk)
    best = result.best()
    return {
        "encoding": best.encoding if best else None,
        "confidence": best.raw['confidence'] if best else 0.0
    }


def filter_iso_8859_1( byte_string ):
    # Define a translation table to replace non-ISO-8859-1 characters with empty bytes
    translation_table = bytearray.maketrans(b'', b'', bytes(range(128, 256)))

    # Use bytes.translate() to apply the translation table
    filtered_bytes = byte_string.translate(translation_table)
    
    return filtered_bytes


def detect_encoding_lines( file_path : str, max_rows : int = 100000 ):
    file = open(file_path, 'rb')

    encodings = {}
    count_rows = 0
    for line in file:        
        if count_rows >= max_rows:
            break
        count_rows += 1
        
        # Update the encoding and confidence based on the line
        result = detect_charset(line)
        line_encoding = result['encoding']

        if line_encoding not in encodings:
            encodings[line_encoding] = 1
        else:
            encodings[line_encoding] += 1
    file.close()

    # Eliminate ASCII
    if 'ASCII' in encodings:
        count_rows -= encodings['ASCII']
        del encodings['ASCII']
        
    # GET BEST ENCODING
    confidence = 0
    encoding = None
    for enc in encodings:
        calc_conf = encodings[enc] / count_rows
        
        if calc_conf > confidence:
            encoding = enc
            confidence = calc_conf

    # Clean
    encodings.clear()
    encodings = None
    
    return encoding, confidence



def test_encoding( file_path : str, encoding : str ) -> bool:
    try:
        file = open(file_path, mode='r', newline='', encoding=encoding)
        content = file.read()
        return True
    except UnicodeDecodeError:
        return False


def detect_encoding( file_path : str, chunck_size : int = 5242880 ):

    # FIRST - TRY UTF-8
    if test_encoding( file_path, 'UTF-8' ) is True:
        return 'UTF-8', 1
    
    # SECOND - TRY ISO-8859-1
    if test_encoding( file_path, 'ISO-8859-1' ) is True:
        return 'ISO-8859-1', 1

    # ELSE - DETECT
    with open(file_path, 'rb') as file:
        chunck = file.read(chunck_size)
        result = detect_charset( chunck )

    encoding = result['encoding']
    confidence = result['confidence']

    if confidence is None or confidence < 0.5:
        encoding = 'UTF-8'
        confidence = 0.0
    
    return encoding, confidence



if __name__ == "__main__":
    # file_path = '/home/eduardo/Documentos/STORAGE/DE28/FILES_RECIEVED/2020/2020/TMS-0001 2020.08 Sped Contribuicoes Original.TXT.txt' 
    file_path = '/home/eduardo/Documentos/EvoBot/.LOCAL_STORAGE/1698334428811x279854093715306020_EA220/FILES_RECIEVED/1698334428811x279854093715306020_EA220_WN_zip/1705340825209x661487892568196900_WN7_76687656000196101210740020190401201904300E869CC214A469EB9883579D36C58257A63CB5A22SPEDEFD.txt' 
    encoding, confidence = detect_encoding( file_path )
    
    print(encoding, confidence)
    
    # if encoding:
    #     print(f"Detected encoding: {encoding} with confidence: {confidence}")
    # else:
    #     print("Encoding detection failed. Could not determine the encoding.")


