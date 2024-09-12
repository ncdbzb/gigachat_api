import nltk
import nltk.translate.bleu_score as bleu
import warnings


def get_bleu_score(candidate_question: str, right_answer: str) -> float:
    """
    Выводит степень схожести проверяемого ответа с заведомо правильным ответом 
    
    :param candidate_question: Ответ, который нужно проверить
    :param right_answer: Правильный ответ
    :return: blue score
    """
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')

    hyp = candidate_question.split()
    ref = right_answer.split()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        score = bleu.sentence_bleu([hyp], ref)

    return score
