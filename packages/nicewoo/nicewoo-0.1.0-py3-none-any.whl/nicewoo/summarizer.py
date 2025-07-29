from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

def summarize_text(text: str, sentence_count: int = 3) -> str:
    """
    텍스트 요약 (Sumy LSA 기반)

    Args:
        text (str): 입력 텍스트
        sentence_count (int): 요약할 문장 수

    Returns:
        str: 요약된 텍스트
    """
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentence_count)
    return " ".join(str(sentence) for sentence in summary)
