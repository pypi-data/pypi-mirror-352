from nicewoo.stopwords import remove_stopwords

def test_remove_stopwords():
    text = "This is a simple test sentence."
    result = remove_stopwords(text)
    assert "is" not in result.lower()
    assert "this" not in result.lower()  # 불용어니까 없어야 함
