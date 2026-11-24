"""CLI: python -m ingest --source data/sample_docs --collection my-docs"""
import argparse
from pathlib import Path

from .chunker import chunk_pages
from .embedder import Embedder
from .indexer import Indexer
from .loader import load_folder
from .quality import build_report, write_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest documents into a vector index.")
    parser.add_argument("--source", default="data/sample_docs",
                        help="Folder containing documents (PDF, Markdown, HTML)")
    parser.add_argument("--collection", default="my-docs",
                        help="Chroma collection name")
    parser.add_argument("--chunk-size", type=int, default=800)
    parser.add_argument("--overlap", type=int, default=100)
    parser.add_argument("--persist-dir", default="./chroma_db")
    args = parser.parse_args()

    pages = load_folder(Path(args.source))
    print(f"Loaded {len(pages)} pages from {args.source}")

    chunks = chunk_pages(pages, chunk_size=args.chunk_size, overlap=args.overlap)
    print(f"Produced {len(chunks)} chunks")

    embedder = Embedder()
    embeddings = embedder.embed([c.text for c in chunks])
    print(f"Embedded {len(embeddings)} chunks")

    indexer = Indexer(persist_dir=args.persist_dir)
    collection = indexer.get_collection(args.collection)
    added, duplicates = indexer.add(collection, chunks, embeddings)
    print(f"Indexed {added} chunks ({duplicates} duplicates dropped)")

    report = build_report(pages, chunks, added, duplicates)
    out = Path("reports/reconciliation.md")
    write_report(report, out)
    print(f"Report written to {out}")


if __name__ == "__main__":
    main()
