import time
from langchain.chains import RetrievalQA
from langchain.chat_models.gigachat import GigaChat
from gigachatAPI.config_data.config import load_config, Config
from gigachatAPI.chromadb.chromadb_handler import get_chroma
from gigachatAPI.prompts.prompt_templates.qna_new import custom_rag_prompt
from gigachatAPI.utils.help_methods import get_tokens
from gigachatAPI.logs.logs import logger_info


async def get_answer(
        filename: str,
        question_list: list[str],
) -> str:
    config: Config = await load_config()

    giga: GigaChat = GigaChat(credentials=config.GIGA_CREDENTIALS, verify_ssl_certs=False)

    start_time = time.time()

    logger_info.info(f'Всего вопросов: {len(question_list)}')

    tokens_result = 0
    final_res = ''
    for q_num, que in enumerate(question_list, start=1):
        dita_length = 0
        question_start_time = time.time()

        vectordb = await get_chroma(filename)

        docs_with_scores = vectordb.similarity_search_with_score(que, k=6)
        scores = [d[1] for d in docs_with_scores]

        logger_info.info(f'Время работы Chroma для вопроса №{q_num}: {time.time() - question_start_time} секунд')
        logger_info.info(f'Similarity scores для релевантных документов: {scores}')

        # chain = RetrievalQA.from_chain_type(
        #     llm=giga,
        #     retriever=vectordb.as_retriever(
        #         # search_type="similarity",
        #         # search_kwargs={"k": 1}
        #     )
        # )
        chain = RetrievalQA.from_chain_type(
            llm=giga,
            # chain_type="stuff",
            retriever=vectordb.as_retriever(
                # search_type="similarity",
                search_kwargs={"k": 6}
            ),
            # verbose=True,
            chain_type_kwargs={
                # "verbose": True,
                "prompt": custom_rag_prompt
            }
        )
        gigachat_start_time = time.time()

        qa_chain = await chain.ainvoke({"query": que})
        result = qa_chain['result']

        logger_info.info(f'Время работы GigaChat для вопроса №{q_num}: {time.time() - gigachat_start_time} секунд')

        final_res += f'Вопрос {q_num}: {que}\nОтвет: {result}\n\n'

        tokens = await get_tokens(dita_length, len(result))
        tokens_result += tokens

        logger_info.info(f'Потраченные Токены для вопроса №{q_num}: {tokens}')
        logger_info.info(f'Общее время для вопроса №{q_num}: {time.time() - question_start_time} секунд\n')
    logger_info.info(f'Общее количество потраченных Токенов: {tokens_result}')
    logger_info.info(f'Общее время: {time.time() - start_time}')

    return final_res
