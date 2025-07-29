from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def remove_stopwords(text: str, lang: str = 'english') -> str:
    """
    불용어를 제거한 텍스트를 반환합니다.

    Args:
        text (str): 입력 텍스트
        lang (str): 언어 (기본: 'english')

    Returns:
        str: 불용어가 제거된 텍스트
    """
    stop_words = set(stopwords.words(lang))
    words = word_tokenize(text)
    filtered = [w for w in words if w.lower() not in stop_words]
    return ' '.join(filtered)
