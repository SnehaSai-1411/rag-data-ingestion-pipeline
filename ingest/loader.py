"""Load PDFs, Markdown, and HTML files from a folder into text records."""
from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup
from pypdf import PdfReader


@dataclass
class Page:
    source: str   # file name, e.g. "rag-paper.pdf"
    page: int     # 1-based page number (1 for Markdown/HTML, which have no pages)
    text: str     # extracted text (may be empty for scanned/image pages)


def load_pdf(path: Path) -> list[Page]:
    reader = PdfReader(str(path))
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        pages.append(Page(source=path.name, page=i, text=text))
    return pages


def load_markdown(path: Path) -> list[Page]:
    text = path.read_text(encoding="utf-8").strip()
    return [Page(source=path.name, page=1, text=text)]


def load_html(path: Path) -> list[Page]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    # Drop non-content elements so scripts/styles never become chunks.
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator="\n\n").strip()
    return [Page(source=path.name, page=1, text=text)]


def load_folder(folder: Path) -> list[Page]:
    pages: list[Page] = []
    for pdf in sorted(folder.glob("*.pdf")):
        pages.extend(load_pdf(pdf))
    for md in sorted(folder.glob("*.md")):
        pages.extend(load_markdown(md))
    for html in sorted(folder.glob("*.html")):
        pages.extend(load_html(html))
    return pages
