import spacy
from collections import Counter
# !pip install spacy
# !python -m spacy download ru_core_news_sm

# Загрузка модели для русского языка
nlp = spacy.load("ru_core_news_sm")

def lemmatize_text(text):
    """ Лемматизация текста с использованием spaCy """
    doc = nlp(text)
    return ' '.join(token.lemma_ for token in doc if not token.is_punct and not token.is_space)

def tokenize_text(text):
    """ Токенизация текста с использованием spaCy """
    doc = nlp(text)
    return [token.text for token in doc if not token.is_punct and not token.is_space]

def calculate_rouge_metrics(reference_text, generated_text):
    """ Рассчитывает метрики ROUGE-1, ROUGE-2 и ROUGE-L """
    reference_tokens = tokenize_text(reference_text)
    generated_tokens = tokenize_text(generated_text)

    # ROUGE-1
    reference_counter = Counter(reference_tokens)
    generated_counter = Counter(generated_tokens)
    num_matching_unigrams = sum((reference_counter & generated_counter).values())
    total_reference_unigrams = len(reference_tokens)
    total_generated_unigrams = len(generated_tokens)
    rouge_1_recall = num_matching_unigrams / total_reference_unigrams if total_reference_unigrams > 0 else 0
    rouge_1_precision = num_matching_unigrams / total_generated_unigrams if total_generated_unigrams > 0 else 0
    rouge_1_f1 = (2 * rouge_1_precision * rouge_1_recall) / (rouge_1_precision + rouge_1_recall) if (rouge_1_precision + rouge_1_recall) > 0 else 0

    # ROUGE-2
    def get_ngrams(tokens, n):
        return [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]

    reference_bigrams = get_ngrams(reference_tokens, 2)
    generated_bigrams = get_ngrams(generated_tokens, 2)

    reference_bigram_counter = Counter(reference_bigrams)
    generated_bigram_counter = Counter(generated_bigrams)
    num_matching_bigrams = sum((reference_bigram_counter & generated_bigram_counter).values())
    total_reference_bigrams = len(reference_bigrams)
    total_generated_bigrams = len(generated_bigrams)
    rouge_2_recall = num_matching_bigrams / total_reference_bigrams if total_reference_bigrams > 0 else 0
    rouge_2_precision = num_matching_bigrams / total_generated_bigrams if total_generated_bigrams > 0 else 0
    rouge_2_f1 = (2 * rouge_2_precision * rouge_2_recall) / (rouge_2_precision + rouge_2_recall) if (rouge_2_precision + rouge_2_recall) > 0 else 0

    # ROUGE-L
    def lcs_length(X, Y):
        m = len(X)
        n = len(Y)
        L = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            for j in range(n + 1):
                if i == 0 or j == 0:
                    L[i][j] = 0
                elif X[i - 1] == Y[j - 1]:
                    L[i][j] = L[i - 1][j - 1] + 1
                else:
                    L[i][j] = max(L[i - 1][j], L[i][j - 1])

        return L[m][n]

    lcs_len = lcs_length(reference_tokens, generated_tokens)
    total_reference_tokens = len(reference_tokens)
    rouge_l_recall = lcs_len / total_reference_tokens if total_reference_tokens > 0 else 0
    rouge_l_precision = lcs_len / len(generated_tokens) if len(generated_tokens) > 0 else 0
    rouge_l_f1 = (2 * rouge_l_precision * rouge_l_recall) / (rouge_l_precision + rouge_l_recall) if (rouge_l_precision + rouge_l_recall) > 0 else 0

    return {
        "rouge_1_recall": rouge_1_recall,
        "rouge_1_precision": rouge_1_precision,
        "rouge_1_f1": rouge_1_f1,
        "rouge_2_recall": rouge_2_recall,
        "rouge_2_precision": rouge_2_precision,
        "rouge_2_f1": rouge_2_f1,
        "rouge_l_recall": rouge_l_recall,
        "rouge_l_precision": rouge_l_precision,
        "rouge_l_f1": rouge_l_f1
    }
