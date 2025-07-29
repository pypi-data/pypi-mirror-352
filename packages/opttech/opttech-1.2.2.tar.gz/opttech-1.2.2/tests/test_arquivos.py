import os
import opttech
import zipfile

def test_map_files(tmp_path):
    # Cria uma estrutura de pastas de teste
    (tmp_path / "subpasta").mkdir()
    arquivo1 = tmp_path / "arquivo1.txt"
    arquivo2 = tmp_path / "subpasta" / "arquivo2.txt"
    arquivo1.write_text("conteúdo")
    arquivo2.write_text("conteúdo")

    arquivos = opttech.map_files(str(tmp_path))
    assert str(arquivo1) in arquivos
    assert str(arquivo2) in arquivos
    assert len(arquivos) == 2


def test_decompressor( tmp_path ):
    # Cria um arquivo zip de teste
    zip_path = tmp_path / "teste.zip"
    with zipfile.ZipFile( zip_path, 'w' ) as zipf:
        zipf.writestr("arquivo.txt", "content")

    zip_path = tmp_path / "teste_2.zip"
    with zipfile.ZipFile( zip_path, 'w' ) as zipf:
        zipf.writestr("arquivo_2.txt", "content")

    # Testa a função deep_decompressor
    ret = opttech.decompressor(str(tmp_path))
    decompressed_files = opttech.map_files(tmp_path)
    print('arquivos:', decompressed_files)

    assert str(tmp_path / "teste_zip" / "arquivo.txt" ) in decompressed_files
    assert str(tmp_path / "teste_2_zip" / "arquivo_2.txt" ) in decompressed_files
    assert os.path.exists( str(tmp_path / "ZIP_FOLDER") )
    assert not os.path.exists( str(tmp_path / "BADZIP_FOLDER") )


def test_compressor( tmp_path ):
    # Cria um arquivo .txt de teste
    txt_file = tmp_path / "teste.txt"
    txt_file.write_text("content")

    txt_file_2 = tmp_path / "teste_2.txt"
    txt_file_2.write_text("content")

    # Testa a função zipper
    zip_name='zipped_files.zip'
    zipped_files = opttech.compressor(str(tmp_path), zip_name=zip_name)

    assert str(tmp_path / "zipped_files.zip") in zipped_files
    assert len(zipped_files) == 1



# # # Testar no debug do vscode o deep_decompressor com arquivo na pasta "/home/eduardo/Packages/opttech/tests/arquivos"
# if __name__ == '__main__':
#     # Teste rápido
#     folder_path = '/home/eduardo/Packages/opttech/tests/arquivos'
#     opttech.deep_decompressor(folder_path)
#     print('Decompressão completa.')
    
#     # Teste de compressão
#     folder_path = '/home/eduardo/Packages/opttech/tests/arquivos'
#     zip_paths = opttech.zipper(folder_path, zip_folder='/home/eduardo/Packages/opttech/tests', zip_name='1243')
#     print('Arquivos comprimidos:', zip_paths)
