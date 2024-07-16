import os
import shutil
from gigachatAPI.chromadb.vectordb_manager import VectordbManager


async def delete_doc(doc_name) -> None:
    if doc_name in ('chroma', 'temp'):
        raise ValueError('Forbidden')
    
    delete_path_file = os.path.join('gigachatAPI', 'data', doc_name)

    if os.path.exists(delete_path_file) and os.path.isdir(delete_path_file):
        shutil.rmtree(delete_path_file)
        print(f'{doc_name} has been deleted')

    vectordb_manager = VectordbManager()
    vectordb_manager.delete_collection(doc_name)
    return 
