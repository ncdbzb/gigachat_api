import nltk
from nltk.translate.meteor_score import meteor_score


nltk.download('wordnet')

def get_meteor_score(reference: str, hypothesis: str) -> float:
    return meteor_score([reference.split()], hypothesis.split())
