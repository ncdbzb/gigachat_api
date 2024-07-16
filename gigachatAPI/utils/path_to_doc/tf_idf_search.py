from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


async def tf_idf_search(texts: list[str], user_query: str) -> tuple[int, str]:
    original_dict = {}

    for i, j in enumerate(texts, start=1):
        original_dict[i] = j
    vectorizer = TfidfVectorizer()

    tfidf_matrix = vectorizer.fit_transform(list(original_dict.values()) + [user_query])

    cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()

    tfidf_matches = sorted(enumerate(cosine_similarities), key=lambda x: x[1], reverse=True)

    for match in tfidf_matches[:3]:
        index, similarity = match
        file_id = list(original_dict.keys())[index]
        # print(f"ID: {file_id}, Описание: {original_dict[file_id]}, Сходство: {similarity:.4f}")

        return file_id, original_dict[file_id]
