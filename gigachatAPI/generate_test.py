import os
import time
from random import choice
from langchain.chat_models.gigachat import GigaChat
from gigachatAPI.config_data.config_data import *
from gigachatAPI.config_data.config import load_config, Config
from gigachatAPI.prompts.create_prompts import create_prompt
from gigachatAPI.utils.output_parser import get_questions_dict
from gigachatAPI.process_files.get_result_docs_list import get_result_docs_list
from gigachatAPI.logs.logs import logger_info


async def generate_test(
        filename: str
) -> dict:
    config: Config = await load_config()

    giga: GigaChat = GigaChat(credentials=config.GIGA_CREDENTIALS, verify_ssl_certs=False)

    start_time = time.time()

    path_for_splitting = os.path.join('gigachatAPI', 'data', filename)
    split_docs = await get_result_docs_list(path_for_splitting, 'generate_test')

    data_process_time = time.time() - start_time

    prompt = await create_prompt(gen_que_with_answ_prompt_path)

    chain = prompt | giga

    document_length = sum(len(i.page_content) for i in split_docs)
    max_part_doc_len = max(len(i.page_content) for i in split_docs)

    logger_info.info(f'Общая длина загруженного документа: {document_length}')
    logger_info.info(f'Время обработки данных: {data_process_time} секунд\n')

    gigachat_start_time = time.time()

    doc_part = choice(split_docs)
    result = await chain.ainvoke({"text": doc_part})
    questions_dict = await get_questions_dict(result.content + '\n')

    tokens = result.response_metadata['token_usage'].total_tokens

    logger_info.debug(f'Вопрос успешно сгенерирован')
    logger_info.info(f'Токенов потрачено: {tokens}\n')
    logger_info.info(f'Время работы GigaChat: {time.time() - gigachat_start_time} секунд')
    lead_time = time.time() - start_time
    logger_info.info(f'Общее время: {lead_time} секунд')

    result_dict = {
        "result": questions_dict,
        "prompt_path": gen_que_with_answ_prompt_path,
        "tokens": tokens,
        "lead_time": round(lead_time, 3)
    }

    return result_dict
