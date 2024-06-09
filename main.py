import asyncio
import os
import time

from aiohttp import web

from gigachatAPI.answer_questions import get_answer
from gigachatAPI.generate_test import generate_test
from gigachatAPI.process_files.process_paths import process_and_take_path
from gigachatAPI.chromadb.chromadb_handler import initialize_chroma
from gigachatAPI.process_files.get_result_docs_list import get_result_docs_list
from gigachatAPI.utils.delete_doc import delete_doc
from gigachatAPI.utils.help_methods import get_actual_doc_list


async def handle_doc(request):
    start_time = time.time()
    data = await request.post()
    file = data['file']
    doc_name, extension = '.'.join(file.filename.split('.')[:-1]), file.filename.split('.')[-1]
    
    if extension != 'txt':
        save_path = os.path.join('gigachatAPI', 'data', f'{doc_name}.{extension}')
    else:
        save_path = os.path.join('gigachatAPI', 'data', f'{doc_name}', f'{doc_name}.{extension}')
        dir_path = os.path.dirname(save_path)
        os.makedirs(dir_path, exist_ok=True)

    with open(save_path, 'wb') as file_object:
        file_object.write(file.file.read())
    print(f'saved {doc_name}.{extension} with time {time.time() - start_time}')

    path = await process_and_take_path(doc_name, extension, save_path)

    split_docs = await get_result_docs_list(path, doc_name, 'initialize_chroma')

    # vectordb_manager = VectordbManager()
    # vectordb_manager.create_collection(doc_filename, split_docs)
    await initialize_chroma(split_docs, doc_name)
    print(f'time: {time.time() - start_time}')

    return web.json_response({"result": "File was received"})


async def handle_delete_doc(request):
    data = await request.json()
    doc_name = data['doc_name']
    await delete_doc(doc_name)
    return web.json_response({"result": "Doc was deleted"})

async def handle_test(request):
    data = await request.json()
    print("Received data:", data)
    result = await generate_test(data['filename'])
    return web.json_response(result)


async def handle_questions(request):
    data = await request.json()
    print("Received data:", data)
    result = await get_answer(data['filename'], data['question'])
    return web.json_response(result)


async def handle_get_actual_doc_list(request):
    result = await get_actual_doc_list()
    return web.json_response(result)


async def main():
    app = web.Application(client_max_size=100*1024*1024)
    app.router.add_post('/process_data', handle_test)
    app.router.add_post('/process_questions', handle_questions)
    app.router.add_post('/process_doc', handle_doc)
    app.router.add_post('/process_delete_doc', handle_delete_doc)
    app.router.add_post('/process_get_actual_doc_list', handle_get_actual_doc_list)


    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()

    print("gigachatAPI started")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
