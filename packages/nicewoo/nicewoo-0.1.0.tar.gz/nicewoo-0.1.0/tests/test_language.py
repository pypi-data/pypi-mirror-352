from nicewoo.language import detect_language

def test_detect_language():
    assert detect_language("Hello, how are you?") == "en"
    assert detect_language("안녕하세요") == "ko"
