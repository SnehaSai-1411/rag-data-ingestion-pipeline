# rag-data-ingestion-pipeline

Document ingestion pipeline for RAG — PDF, Markdown, and HTML loading, chunking, embeddings, and vector indexing with data-quality checks and a reconciliation report on every run.

## What it does

- Loads PDFs page by page, plus Markdown and HTML files, preserving source + page metadata for citations
- Chunks text on paragraph boundaries (configurable size/overlap)
- Embeds chunks locally with sentence-transformers (all-MiniLM-L6-v2) — no API key needed
- Indexes into a persistent Chroma collection; duplicate chunks dropped by content hash
- Writes a reconciliation report on every run: documents/pages in vs. chunks indexed, per document

## Architecture

```
data/sample_docs/ ──► loader ──► chunker ──► embedder ──► indexer ──► chroma_db/
  (PDF / .md / .html)   │           │            │             │
                        │           │            │             ▼
                        └───────────┴────────────┴──► quality.py
                                                        reports/reconciliation.md
```

Each module does exactly one job: `loader.py` extracts text, `chunker.py`
splits it, `embedder.py` turns chunks into vectors, `indexer.py` stores
them, and `quality.py` reports what went in vs. what got indexed.

## Quickstart

```bash
pip install -r requirements.txt
python -m ingest --source data/sample_docs --collection my-docs
python -m ingest.query "How does the Transformer use self-attention?"
```

## Example

```text
$ python -m ingest.query "How does the Transformer use self-attention?"

[attention-is-all-you-need.pdf p.5 | distance 0.330]
...The Transformer uses multi-head attention in three different ways:
"In encoder-decoder attention" layers, the queries come from the
previous decoder layer...

[attention-is-all-you-need.pdf p.3 | distance 0.394]
Figure 1: The Transformer - model architecture. The Transformer follows
this overall architecture using stacked self-attention and point-wise,
fully connected layers for both the encoder and decoder...

[attention-is-all-you-need.pdf p.2 | distance 0.420]
...computing hidden representations in parallel for all input and
output positions...
```

Real output from the sample docs (35 pages, 171 chunks indexed — see
[`reports/reconciliation.example.md`](reports/reconciliation.example.md)).
Lower distance = closer match. All three top hits come from the
Transformer paper, with page numbers, because source + page metadata is
carried from load time through to the index. A RAG question returns
chunks from `rag-paper.pdf` the same way.

## Design decisions & trade-offs

- **Per-page loading:** citations need page numbers, so metadata is captured at load time, never reconstructed later. Markdown/HTML have no pages, so they load as page 1.
- **Paragraph-aware chunking with overlap fallback:** keeps semantic units whole; overlap only where a hard split is unavoidable. Fixed 800/100 defaults are a sane start for dense text, not a measured optimum — Project 3 (evaluation harness) is where that gets tested.
- **Content-hash dedupe:** identical chunks (repeated boilerplate, double-added files) are dropped and counted in the report, so the report can prove what happened.
- **Local embeddings:** zero API cost and fully reproducible; the embedder is one class, swappable for an API model later. The trade-off is a smaller model than API embeddings — fine for a personal project, worth re-measuring at scale.

## What I would add next

- OCR path for scanned PDFs (empty pages are counted today, not yet read)
- Incremental ingestion (skip unchanged files by hash)
- DOCX support
- A GCS/S3 source in addition to a local folder
