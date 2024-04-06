import os
import shutil


async def delete_doc(doc_name) -> None:
    delete_path_file = os.path.join('gigachatAPI', 'data', doc_name)
    delete_path_chroma = os.path.join('gigachatAPI', 'data', 'chroma', doc_name)
    if os.path.exists(delete_path_file) and os.path.isdir(delete_path_file):
        shutil.rmtree(delete_path_file)
        print(f'{doc_name} has been deleted')
    if os.path.exists(delete_path_chroma) and os.path.isdir(delete_path_chroma):
        shutil.rmtree(delete_path_chroma)
        print(f'chroma/{doc_name} has been deleted')
    return 
