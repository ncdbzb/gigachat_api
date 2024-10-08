import pytest
import asyncio
from langchain_community.chat_models.gigachat import GigaChat
from gigachatAPI.config_data.config import load_config, Config
from gigachatAPI.metrics.sentence_bleu.sentence_bleu import get_bleu_score
from gigachatAPI.metrics.rouge.rouge_metrics import calculate_rouge_metrics
from gigachatAPI.utils.path_to_doc.path_to_doc import get_path_to_doc
from gigachatAPI.chromadb.vectordb_manager import VectordbManager
from gigachatAPI.prompts.create_prompts import qna_prompt
from gigachatAPI.logs.logs import upload_doc_info
from tests.data_for_check import get_data_from_csv, log_result_to_csv


data = get_data_from_csv(limit=2)

# Список вопросов на проверку
questions = data['questions']

# Список ожидаемых ответов
expected_answers = data['ref_answers']

# Список ожидаемых dita
expected_dita_paths = data['ref_dita']

ids = [f"Test case #{i}" for i in range(len(questions))]


@pytest.fixture
def giga():
    """Создание экземпляра GigaChat"""
    config: Config = load_config()

    giga: GigaChat = GigaChat(credentials=config.GIGA_CREDENTIALS, verify_ssl_certs=False, verbose=True)
    yield giga


@pytest.fixture
def vectordb_manager():
    """Подключение к векторной базе данных"""
    manager = VectordbManager()
    yield manager


@pytest.fixture
def filename():
    """Название документации, по которой проводится тестирование"""
    return "DATAPK_ITM_VERSION_1_7"


@pytest.mark.parametrize("question, expected_answer, expected_dita_path", zip(questions, expected_answers, expected_dita_paths), ids=ids)
def test_answers(filename, question, expected_answer, expected_dita_path, vectordb_manager, giga):
    try:

        docs, sim_scores = vectordb_manager.sim_search(filename, question, 4, with_sim_scores=True)
        assert docs, f'Введено неверное значение {filename} или коллекция не создана'
        try:
            assert sim_scores[0] < 10, f'similarity scores: {sim_scores}, что > 10'
        except AssertionError as e:
            upload_doc_info.error(e)

        response = giga.invoke(qna_prompt.format(question=question, context=docs))
        answer = response.content

        dita_path = asyncio.run(get_path_to_doc(docs, filename, answer))

        try:
            assert dita_path == expected_dita_path, f'Полученный dita файл: {dita_path} не соответствуюет ожидаемому: {expected_dita_path}'
        except AssertionError as e:
            upload_doc_info.error(e)

        bleu_score = get_bleu_score(answer, expected_answer)

        rouge_metrics = calculate_rouge_metrics(expected_answer, answer)


    finally:
        log_result_to_csv(
            filename,
            question,
            ', '.join(map(str, sim_scores)),
            dita_path,
            bleu_score,
            rouge_metrics['rouge_1_f1'],
            rouge_metrics['rouge_2_f1'],
            rouge_metrics['rouge_l_f1'],
            answer
        )
