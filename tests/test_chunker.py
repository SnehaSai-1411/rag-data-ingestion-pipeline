from ingest.chunker import chunk_pages, chunk_text
from ingest.loader import Page


def test_short_text_one_chunk():
    assert chunk_text("hello world", chunk_size=800, overlap=100) == ["hello world"]


def test_long_paragraph_is_split_with_overlap():
    text = "a" * 2000
    chunks = chunk_text(text, chunk_size=800, overlap=100)
    assert len(chunks) >= 3
    assert all(len(c) <= 800 for c in chunks)


def test_empty_pages_produce_no_chunks():
    pages = [Page(source="x.pdf", page=1, text=""),
             Page(source="x.pdf", page=2, text="real content")]
    chunks = chunk_pages(pages)
    assert len(chunks) == 1
    assert chunks[0].page == 2


def test_chunk_indices_increment_per_source():
    pages = [Page(source="x.pdf", page=1, text="para one\n\npara two"),
             Page(source="x.pdf", page=2, text="para three")]
    chunks = chunk_pages(pages, chunk_size=10, overlap=2)
    assert [c.chunk_index for c in chunks] == list(range(len(chunks)))
