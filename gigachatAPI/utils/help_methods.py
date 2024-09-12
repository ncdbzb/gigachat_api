import zipfile
import os
from gigachatAPI.logs.logs import upload_doc_info


async def extract_zip(zipfile_path: str, extracted_files_path: str) -> None:
    with zipfile.ZipFile(zipfile_path, 'r') as zip_ref:
        zip_ref.extractall(extracted_files_path)


async def get_doc_length(path_doc: str) -> int:
    with open(path_doc, 'r', encoding='utf-8') as file:
        content = file.read()
        return len(content)
    

def rename_directory(old_name: str, new_name: str) -> None:
    old_path_initial = os.path.join('gigachatAPI', 'data', 'initial_docs', old_name)
    new_path_initial = os.path.join('gigachatAPI', 'data', 'initial_docs', new_name)
    old_path_test_system = os.path.join('gigachatAPI', 'data', 'test_system_docs', f'{old_name}.txt')
    new_path_test_system = os.path.join('gigachatAPI', 'data', 'test_system_docs', f'{new_name}.txt')
    
    os.rename(old_path_initial, new_path_initial)
    upload_doc_info.debug(f'{old_path_initial} was renamed to {new_path_initial}')
    os.rename(old_path_test_system, new_path_test_system)
    upload_doc_info.debug(f'{old_path_test_system} was renamed to {new_path_test_system}')

    files = os.listdir(new_path_initial)
    
    if len(files) == 1:
        file_name = files[0]
        if file_name == f"{old_name}.txt":
            old_file_path = os.path.join(new_path_initial, file_name)
            new_file_path = os.path.join(new_path_initial, f"{new_name}.txt")
            os.rename(old_file_path, new_file_path)
    
    return


def documents_to_txt(filename: str, split_docs: list, delimiter='|*|*|*|') -> None:
    with open(os.path.join('gigachatAPI', 'data', 'test_system_docs', f'{filename}.txt'), 'a', encoding='utf-8') as file:
        for line in split_docs:
            file.write(line.page_content + delimiter)
    
    return


def get_split_docs_from_txt(filename: str, delimiter='|*|*|*|') -> list[str]:
    with open(os.path.join('gigachatAPI', 'data', 'test_system_docs', f'{filename}.txt'), 'r', encoding='utf-8') as file:
        content = file.read()
    
    strings = content.split(delimiter)
    split_docs = [s.strip() for s in strings if s.strip()]
    
    return split_docs
    