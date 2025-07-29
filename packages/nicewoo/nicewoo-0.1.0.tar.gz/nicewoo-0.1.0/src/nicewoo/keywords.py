from sklearn.feature_extraction.text import TfidfVectorizer

def extract_keywords(text: str, top_n: int = 5):
    """
    TF-IDF 기반 키워드 상위 top_n개 추출

    Args:
        text (str): 입력 텍스트
        top_n (int): 추출할 키워드 개수

    Returns:
        List[str]: 키워드 리스트
    """
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([text])
    scores = zip(vectorizer.get_feature_names_out(), tfidf_matrix.toarray()[0])
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_scores[:top_n]]
