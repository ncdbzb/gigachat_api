import os
import time
from random import sample
from langchain_community.chat_models.gigachat import GigaChat
from gigachatAPI.config_data.config import load_config, Config
from gigachatAPI.prompts.create_prompts import gen_que_prompt
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

    chain = gen_que_prompt | giga

    logger_info.info(f'Тест по документации: {filename}')

    logger_info.info(f'Время обработки данных: {data_process_time} секунд')

    gigachat_start_time = time.time()

    questions_dict = {}
    tokens = 0
    elems_num = 5 if len(split_docs) >= 5 else len(split_docs)
    for doc_part in sample(split_docs, elems_num): 
        result = await chain.ainvoke({"text": doc_part})
        tokens += result.response_metadata['token_usage'].total_tokens 
        questions_dict = await get_questions_dict(result.content + '\n')
        if 'result' in questions_dict.keys():
            logger_info.info(f'Тест успешно сгенерирован')
            break
        logger_info.debug(f'Ошибка! Генериурю тест заново...')

    if 'error' in questions_dict.keys():
        logger_info.info(f'Тест сгенерирован с ошибкой')
    logger_info.info(f'Токенов потрачено: {tokens}')
    gigachat_time = time.time() - gigachat_start_time
    logger_info.info(f'Время работы GigaChat: {gigachat_time} секунд')
    lead_time = time.time() - start_time
    logger_info.info(f'Общее время: {lead_time} секунд\n\n')

    result_dict = {
        "result": questions_dict,
        "prompt_path": 'gigachatAPI/prompts/prompt_templates/gen_que.py',
        "tokens": tokens,
        "total_time": round(lead_time, 3),
        "gigachat_time": round(gigachat_time, 3)
    }

    return result_dict
