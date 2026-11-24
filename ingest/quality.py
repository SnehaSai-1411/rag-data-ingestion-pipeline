"""Build a reconciliation report: what went in vs. what got indexed."""
from pathlib import Path


def build_report(pages, chunks, added: int, duplicates: int) -> dict:
    sources = sorted({p.source for p in pages})
    per_source = {}
    for src in sources:
        per_source[src] = {
            "pages": sum(1 for p in pages if p.source == src),
            "empty_pages": sum(1 for p in pages if p.source == src and not p.text),
            "chunks": sum(1 for c in chunks if c.source == src),
        }
    return {
        "documents": len(sources),
        "pages_total": len(pages),
        "pages_empty": sum(1 for p in pages if not p.text),
        "chunks_produced": len(chunks),
        "chunks_indexed": added,
        "duplicates_dropped": duplicates,
        "per_source": per_source,
    }


def write_report(report: dict, out_path: Path) -> None:
    lines = [
        "# Ingestion Reconciliation Report",
        "",
        f"- Documents processed: {report['documents']}",
        f"- Pages read: {report['pages_total']} ({report['pages_empty']} empty)",
        f"- Chunks produced: {report['chunks_produced']}",
        f"- Chunks indexed: {report['chunks_indexed']}",
        f"- Duplicates dropped: {report['duplicates_dropped']}",
        "",
        "| Document | Pages | Empty pages | Chunks |",
        "|---|---|---|---|",
    ]
    for src, s in report["per_source"].items():
        lines.append(f"| {src} | {s['pages']} | {s['empty_pages']} | {s['chunks']} |")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
