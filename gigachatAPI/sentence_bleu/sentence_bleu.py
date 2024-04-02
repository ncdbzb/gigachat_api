import nltk
import nltk.translate.bleu_score as bleu
import warnings


from gigachatAPI.sentence_bleu.bleu_config import references


def get_bleu_score(candidate: str, prepared_question: str):
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')

    hyp = candidate.split()
    ref = references[prepared_question].split()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        score = bleu.sentence_bleu([hyp], ref)

    return score
