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
        que: str,
) -> dict:
    config: Config = await load_config()

    giga: GigaChat = GigaChat(credentials=config.GIGA_CREDENTIALS, verify_ssl_certs=False)

    start_time = time.time()

    question_start_time = time.time()

    vectordb = await get_chroma(filename)

    sim_scores = [d[1] for d in await vectordb.asimilarity_search_with_score(que, k=6)]
    # rel_scores = [d[1] for d in await vectordb.asimilarity_search_with_relevance_scores(que, k=6)]

    logger_info.info(f'Время работы Chroma: {time.time() - question_start_time} секунд')
    logger_info.info(f'Similarity scores для выбранных документов: {sim_scores}')
    # logger_info.info(f'Relevance scores для выбранных документов: {rel_scores}')

    chain = RetrievalQA.from_chain_type(
        llm=giga,
        retriever=vectordb.as_retriever(
            # search_type="similarity_score_threshold",
            search_kwargs={"k": 6}
        ),
        return_source_documents=True,
        # verbose=True,
        chain_type_kwargs={
            # "verbose": True,
            "prompt": custom_rag_prompt
        }
    )

    gigachat_start_time = time.time()
    qa_chain = await chain.ainvoke({"query": que})
    answer, source_documents = qa_chain['result'], qa_chain['source_documents']

    tokens = sum(map(lambda x: x.tokens, await giga.atokens_count(
        [i.page_content for i in source_documents] + [custom_rag_prompt.template, que, answer]
    )))

    logger_info.info(f'Время работы GigaChat: {time.time() - gigachat_start_time} секунд')
    logger_info.info(f'Токенов потрачено: {tokens}')
    lead_time = time.time() - start_time
    logger_info.info(f'Общее время: {lead_time}')

    result = {
        "result": {
            "question": que,
            "answer": answer
        },
        "prompt_path": 'gigachatAPI/prompts/prompt_templates/qna_new.py',
        "tokens": tokens,
        "lead_time": round(lead_time, 3),
        "metrics": sim_scores
    }

    return result
