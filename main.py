import asyncio
import os
import time

from aiohttp import web

from gigachatAPI.rag.answer_questions import get_answer
from gigachatAPI.generate_test import generate_test
from gigachatAPI.process_files.process_paths import process_and_take_path
from gigachatAPI.chromadb.vectordb_manager import VectordbManager
from gigachatAPI.process_files.get_result_docs_list import get_result_docs_list, CHUNK_SIZE
from gigachatAPI.utils.delete_doc import delete_doc
from gigachatAPI.utils.get_actual_docs import get_actual_doc_list
from gigachatAPI.utils.help_methods import rename_directory, documents_to_txt
from gigachatAPI.logs.logs import upload_doc_info


async def handle_doc(request):
    start_time = time.time()
    data = await request.post()
    file = data['file']
    doc_name, extension = '.'.join(file.filename.split('.')[:-1]), file.filename.split('.')[-1]
    
    if extension != 'txt':
        save_path = os.path.join('gigachatAPI', 'data', 'initial_docs', f'{doc_name}.{extension}')
    else:
        save_path = os.path.join('gigachatAPI', 'data', 'initial_docs', f'{doc_name}', f'{doc_name}.{extension}')
        dir_path = os.path.dirname(save_path)
        os.makedirs(dir_path, exist_ok=True)

    with open(save_path, 'wb') as file_object:
        file_object.write(file.file.read())
    upload_doc_info.debug(f'saved {doc_name}.{extension} with time {time.time() - start_time}')

    path = await process_and_take_path(doc_name, extension, save_path)

    split_docs_for_chroma = await get_result_docs_list(path, doc_name, 'initialize_chroma')
    split_docs_for_test_system = await get_result_docs_list(path, doc_name, 'generate_test')

    documents_to_txt(doc_name, split_docs_for_test_system)

    vectordb_manager = VectordbManager()
    vectordb_manager.create_collection(doc_name, split_docs_for_chroma, use_cycle=False)
    upload_doc_info.debug(f'time: {time.time() - start_time}')

    return web.json_response({
    "result": "success",
    "info": {
        "chunk_size": CHUNK_SIZE,
        "embedding_model": vectordb_manager.embeddings.__class__.__name__
        }
    })


async def handle_delete_doc(request):
    data = await request.json()
    doc_name = data['doc_name']
    await delete_doc(doc_name)
    return web.json_response({"result": "Doc was deleted"})


async def handle_test(request):
    data = await request.json()
    result = await generate_test(data['filename'])
    return web.json_response(result)


async def handle_questions(request):
    data = await request.json()
    result = await get_answer(data['filename'], data['question'])
    return web.json_response(result)


async def handle_get_actual_doc_list(request):
    result = await get_actual_doc_list()
    return web.json_response(result)


async def handle_change_doc_name(request):
    data = await request.json()
    vectordb_manager = VectordbManager()
    vectordb_manager.change_collection_name(data['cur_name'], data['new_name'])
    rename_directory(data['cur_name'], data['new_name'])
    return web.json_response({"result": "Name has been changed"})


async def handle_add_data(request):
    data = await request.post()
    file = data['file']
    doc_name = '.'.join(file.filename.split('.')[:-1])
    save_path = os.path.join('gigachatAPI', 'data', 'temp', f'{file.filename}')
    with open(save_path, 'wb') as file_object:
        file_object.write(file.file.read())

    split_docs = await get_result_docs_list(save_path, doc_name, 'initialize_chroma')
    split_docs_for_chroma = list(map(lambda x: x.page_content, split_docs))

    vectordb_manager = VectordbManager()
    vectordb_manager.add_data(doc_name, split_docs_for_chroma)
    upload_doc_info.debug(f'new data was added to {doc_name} (chroma)')

    split_docs_for_test_system = await get_result_docs_list(save_path, doc_name, 'generate_test')
    documents_to_txt(doc_name, split_docs_for_test_system)
    upload_doc_info.debug(f'new data was added to {doc_name} (txt)')
    
    await asyncio.to_thread(os.remove, save_path)
    return web.json_response({"result": "Data was added"})


async def main():
    app = web.Application(client_max_size=100*1024*1024)
    app.router.add_post('/process_data', handle_test)
    app.router.add_post('/process_questions', handle_questions)
    app.router.add_post('/process_doc', handle_doc)
    app.router.add_post('/process_delete_doc', handle_delete_doc)
    app.router.add_post('/process_get_actual_doc_list', handle_get_actual_doc_list)
    app.router.add_post('/process_change_doc_name', handle_change_doc_name)
    app.router.add_post('/process_add_data', handle_add_data)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()

    upload_doc_info.debug("gigachatAPI started")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
