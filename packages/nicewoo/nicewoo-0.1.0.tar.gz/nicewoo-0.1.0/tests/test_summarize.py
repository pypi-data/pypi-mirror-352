from nicewoo.summarizer import summarize_text

def test_summarize_text():
    text = (
        "Artificial intelligence is the simulation of human intelligence processes by machines, "
        "especially computer systems. Specific applications of AI include expert systems, natural "
        "language processing, speech recognition, and machine vision. AI is transforming industries "
        "and shaping the future of work and society."
    )
    summary = summarize_text(text, sentence_count=2)
    assert isinstance(summary, str)
    assert len(summary.split(".")) <= 3  # 2 문장 요약 + 마지막 빈 항목
