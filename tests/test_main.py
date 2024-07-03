import pytest
import asyncio
from langchain_community.chat_models.gigachat import GigaChat
from gigachatAPI.config_data.config import load_config, Config
from gigachatAPI.sentence_bleu.sentence_bleu import get_bleu_score
from gigachatAPI.chromadb.vectordb_manager import VectordbManager
from gigachatAPI.prompts.create_prompts import qna_prompt
from tests.data_for_check import question_for_check, right_answers


# Список вопросов на проверку
questions = question_for_check[1:3]

# Список ожидаемых ответов
expected_answers = right_answers[1:3]

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
    return "new_datapk800_tests"


@pytest.mark.parametrize("question, expected_answer", zip(questions, expected_answers), ids=ids)
def test_answers(filename, question, expected_answer, vectordb_manager, giga):

    docs, sim_scores = vectordb_manager.sim_search(filename, question, 4, with_sim_scores=True)
    assert docs, f'Введено неверное значение {filename} или коллекция не создана'
    assert sim_scores[0] < 350, f'similarity scores: {sim_scores}, что > 350'

    response = giga.invoke(qna_prompt.format(question=question, context=docs))
    answer = response.content

    score = get_bleu_score(answer, expected_answer)
    assert score > 0.2, f"Bleu score = {score}, что меньше 0.2"
