import os
from gigachatAPI.logs.logs import upload_doc_info
from gigachatAPI.chromadb.vectordb_manager import VectordbManager


async def get_actual_doc_list():
    data_dir = "gigachatAPI/data/initial_docs"

    all_items = os.listdir(data_dir)

    filtered_dirs = [
        item for item in all_items
        if os.path.isdir(os.path.join(data_dir, item))
    ]

    vectordb_manager = VectordbManager()
    chroma_collections = vectordb_manager.get_list_collections()
    upload_doc_info.debug(chroma_collections)

    # for collection in chroma_collections:
    #     if collection not in filtered_dirs:
    #         raise ValueError('Conflict in data directory')

    return filtered_dirs
