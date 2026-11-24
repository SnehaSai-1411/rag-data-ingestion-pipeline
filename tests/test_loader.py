"""Loader tests: Markdown and HTML support (PDF path is covered by the
sample docs in the end-to-end smoke test and the real run)."""
from pathlib import Path

from ingest.loader import load_folder, load_html, load_markdown


def test_markdown_loads_as_single_page(tmp_path: Path):
    doc = tmp_path / "notes.md"
    doc.write_text("# RAG notes\n\nRetrieval augmented generation grounds answers in documents.\n",
                   encoding="utf-8")
    pages = load_markdown(doc)
    assert len(pages) == 1
    assert pages[0].source == "notes.md"
    assert pages[0].page == 1
    assert "Retrieval augmented generation" in pages[0].text


def test_html_extracts_visible_text_only(tmp_path: Path):
    doc = tmp_path / "page.html"
    doc.write_text(
        "<html><head><style>body { color: red; }</style>"
        "<script>var secret = 1;</script></head>"
        "<body><h1>Chunking</h1><p>Chunks should respect paragraph boundaries.</p></body></html>",
        encoding="utf-8",
    )
    pages = load_html(doc)
    assert len(pages) == 1
    assert pages[0].source == "page.html"
    assert pages[0].page == 1
    assert "Chunks should respect paragraph boundaries" in pages[0].text
    assert "secret" not in pages[0].text
    assert "color: red" not in pages[0].text


def test_load_folder_picks_up_md_and_html(tmp_path: Path):
    (tmp_path / "a.md").write_text("markdown content", encoding="utf-8")
    (tmp_path / "b.html").write_text("<p>html content</p>", encoding="utf-8")
    (tmp_path / "c.txt").write_text("unsupported, should be ignored", encoding="utf-8")
    pages = load_folder(tmp_path)
    assert sorted(p.source for p in pages) == ["a.md", "b.html"]
    assert all(p.page == 1 for p in pages)


def test_empty_markdown_file_produces_empty_page(tmp_path: Path):
    doc = tmp_path / "empty.md"
    doc.write_text("   \n", encoding="utf-8")
    pages = load_markdown(doc)
    assert len(pages) == 1
    assert pages[0].text == ""
