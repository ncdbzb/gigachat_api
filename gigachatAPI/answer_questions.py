import time
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.chat_models.gigachat import GigaChat
from gigachatAPI.config_data.config import load_config, Config
from gigachatAPI.chromadb.chromadb_handler import get_chroma
from gigachatAPI.prompts.create_prompts import qna_prompt
from gigachatAPI.sentence_bleu.sentence_bleu import get_bleu_score
from gigachatAPI.sentence_bleu.bleu_config import ques_for_check, references
from gigachatAPI.logs.logs import logger_info, logger_context
from gigachatAPI.utils.path_to_doc.path_to_doc import get_path_to_doc


async def get_answer(
        filename: str,
        que: str,
        return_path_to_file: bool = True
) -> dict:
    config: Config = load_config()

    giga: GigaChat = GigaChat(credentials=config.GIGA_CREDENTIALS, verify_ssl_certs=False, temperature=0.2, verbose=True)

    start_time = time.time()

    question_start_time = time.time()

    vectordb = await get_chroma(filename)

    logger_info.info(f'Вопрос по документации: {filename}')

    docs_with_scores = await vectordb.asimilarity_search_with_score(que, k=4)
    sim_scores = [d[1] for d in docs_with_scores]
    docs = [d[0].page_content for d in docs_with_scores]
    logger_context.debug(f'Контекст: {docs}')

    logger_info.info(f'Время работы Chroma: {time.time() - question_start_time} секунд')

    chain = RetrievalQA.from_chain_type(
        llm=giga,
        retriever=vectordb.as_retriever(
            # search_type="similarity_score_threshold",
            search_kwargs={"k": 4}
        ),
        return_source_documents=True,
        # verbose=True,
        chain_type_kwargs={
            # "verbose": True,
            "prompt": qna_prompt
        }
    )

    gigachat_start_time = time.time()
    qa_chain = await chain.ainvoke({"query": que})
    answer, source_documents = qa_chain['result'], qa_chain['source_documents']

    # response = await giga.ainvoke(qna_prompt.format(question=que, context=docs))
    # answer = response.content

    gigachat_time = time.time() - gigachat_start_time

    try:
        if return_path_to_file:
            tf_idf_time = time.time()
            most_relevant_dita_file_path = await get_path_to_doc(docs, filename, answer)
            tf_idf_time = time.time() - tf_idf_time
    except Exception:
        return_path_to_file = False

    tokens = sum(map(lambda x: x.tokens, await giga.atokens_count(
        [i.page_content for i in source_documents] + [qna_prompt.template, que, answer]
    )))

    # tokens = response.response_metadata['token_usage'].total_tokens

    logger_info.info(f'Время работы GigaChat: {gigachat_time} секунд')
    
    lead_time = time.time() - start_time
    logger_info.info(f'Общее время: {lead_time}')
    logger_info.info(f'Токенов потрачено: {tokens}')

    metrics_dict = {"similarity_scores": sim_scores}

    logger_info.info(f'Вопрос: {que}')
    logger_info.info(f'Ответ: {answer}')

    if return_path_to_file:
        logger_info.info(f'Путь к документу: {most_relevant_dita_file_path}')
        if tf_idf_time > 1:
            logger_info.warning(f'Время работы tf-idf time: {tf_idf_time}')
        else:
            logger_info.info(f'Время работы tf-idf time: {tf_idf_time}')

    if que in ques_for_check:
        right_answer = references[que]
        bleu_score = get_bleu_score(answer, right_answer)
        metrics_dict.update({"bleu_score": bleu_score})
        logger_info.info(f'bleu score ответа: {bleu_score}')

    logger_info.info(f'Similarity scores для выбранных документов: {sim_scores}\n\n')

    result = {
        "result": {
            "question": que,
            "answer": answer
        },
        "prompt_path": 'gigachatAPI/prompts/prompt_templates/qna_new.py',
        "tokens": tokens,
        "total_time": round(lead_time, 3),
        "gigachat_time": round(gigachat_time, 3),
        "metrics": metrics_dict
    }

    return result
