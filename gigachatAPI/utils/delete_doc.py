import os
import shutil
from gigachatAPI.chromadb.vectordb_manager import VectordbManager
from gigachatAPI.logs.logs import upload_doc_info


async def delete_doc(doc_name) -> None:
    if doc_name in ('chroma', 'temp'):
        raise ValueError('Forbidden')
    
    delete_paths = [os.path.join('gigachatAPI', 'data', 'initial_docs', doc_name),
                    os.path.join('gigachatAPI', 'data', 'test_system_docs', f'{doc_name}.txt')]

    is_deleted: bool = False

    for delete_path_file in delete_paths:
        if os.path.exists(delete_path_file):
            if os.path.isdir(delete_path_file):
                shutil.rmtree(delete_path_file)
                is_deleted = True
            else:
                os.remove(delete_path_file)
                is_deleted = True
        if is_deleted:
            upload_doc_info.debug(f'{delete_path_file} has been deleted')
        else:
            upload_doc_info.warning(f'Something went wrong while deleting file {delete_file_path}')

    vectordb_manager = VectordbManager()
    vectordb_manager.delete_collection(doc_name)
    
    return 
