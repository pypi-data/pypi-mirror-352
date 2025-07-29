from langdetect import detect

def detect_language(text: str) -> str:
    """
    주어진 텍스트의 언어를 감지합니다.

    Args:
        text (str): 입력 텍스트

    Returns:
        str: 언어 코드 (예: 'en', 'ko', 'fr')
    """
    return detect(text)
