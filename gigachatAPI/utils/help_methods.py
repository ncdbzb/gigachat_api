import zipfile
import os


async def extract_zip(zipfile_path: str, extracted_files_path: str) -> None:
    with zipfile.ZipFile(zipfile_path, 'r') as zip_ref:
        zip_ref.extractall(extracted_files_path)


async def get_doc_length(path_doc: str) -> int:
    with open(path_doc, 'r', encoding='utf-8') as file:
        content = file.read()
        return len(content)
    

def rename_directory(old_name: str, new_name: str) -> None:
    old_path = os.path.join('gigachatAPI', 'data', old_name)
    new_path = os.path.join('gigachatAPI', 'data', new_name)
    
    os.rename(old_path, new_path)
    
    files = os.listdir(new_path)
    
    if len(files) == 1:
        file_name = files[0]
        if file_name == f"{old_name}.txt":
            old_file_path = os.path.join(new_path, file_name)
            new_file_path = os.path.join(new_path, f"{new_name}.txt")
            os.rename(old_file_path, new_file_path)
    
    return
