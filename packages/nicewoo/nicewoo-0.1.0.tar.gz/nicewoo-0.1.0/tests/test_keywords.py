from nicewoo.keywords import extract_keywords

def test_extract_keywords():
    text = "Python is great for data science. Python is also great for machine learning."
    keywords = extract_keywords(text, top_n=3)
    assert isinstance(keywords, list)
    assert len(keywords) == 3
    assert all(isinstance(word, str) for word in keywords)
