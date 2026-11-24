"""End-to-end smoke test with a fake embedder: no model download, no
network. Proves load -> chunk -> embed -> index -> retrieve works, and
that a known chunk is retrievable in the top 3."""
import hashlib
import math
import re
from pathlib import Path

from ingest.chunker import chunk_pages
from ingest.indexer import Indexer
from ingest.loader import load_folder


class FakeEmbedder:
    """Deterministic hashed bag-of-words vectors.

    Each word hashes to a dimension; the vector is L2-normalized, so
    cosine similarity behaves like word overlap. Good enough to prove
    the pipeline retrieves the right chunk; not a semantic model.
    """

    DIM = 256

    def _vec(self, text: str) -> list[float]:
        vec = [0.0] * self.DIM
        for word in re.findall(r"[a-z0-9]+", text.lower()):
            idx = int(hashlib.md5(word.encode()).hexdigest(), 16) % self.DIM
            vec[idx] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._vec(t) for t in texts]


def test_full_pipeline_retrieves_known_chunk(tmp_path: Path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "transformers.md").write_text(
        "# The Transformer\n\n"
        "The Transformer uses self-attention to weigh the importance of "
        "different words in a sequence. Self-attention lets the model relate "
        "positions to each other no matter how far apart they are.\n\n"
        "Attention is all you need: the architecture dispenses with recurrence "
        "and convolutions entirely, relying only on attention mechanisms.\n",
        encoding="utf-8",
    )
    (docs / "cooking.md").write_text(
        "# Cooking Pasta\n\n"
        "Boil water with salt, add the pasta, and stir occasionally so the "
        "noodles do not stick together. Drain and toss with sauce.\n",
        encoding="utf-8",
    )

    pages = load_folder(docs)
    assert len(pages) == 2
    chunks = chunk_pages(pages)
    assert len(chunks) >= 2

    embedder = FakeEmbedder()
    embeddings = embedder.embed([c.text for c in chunks])

    indexer = Indexer(persist_dir=str(tmp_path / "chroma_db"))
    collection = indexer.get_collection("smoke-test")
    added, duplicates = indexer.add(collection, chunks, embeddings)
    assert added == len(chunks)
    assert duplicates == 0

    q_emb = embedder.embed(["How does the Transformer use self-attention?"])[0]
    results = collection.query(query_embeddings=[q_emb], n_results=3)
    top_sources = [m["source"] for m in results["metadatas"][0]]
    top_docs = results["documents"][0]
    assert "transformers.md" in top_sources
    assert any("self-attention" in d for d in top_docs)


def test_duplicate_chunks_are_dropped(tmp_path: Path):
    # Build the duplicate pair directly: the chunker legitimately merges
    # two short identical paragraphs into one chunk, so dedupe is tested
    # at the indexer level, where it lives.
    from ingest.chunker import Chunk

    chunks = [
        Chunk(source="a.md", page=1, chunk_index=0, text="same text"),
        Chunk(source="a.md", page=1, chunk_index=1, text="same text"),
        Chunk(source="a.md", page=1, chunk_index=2, text="different text"),
    ]
    embedder = FakeEmbedder()
    indexer = Indexer(persist_dir=str(tmp_path / "chroma_db"))
    collection = indexer.get_collection("dup-test")
    added, duplicates = indexer.add(
        collection, chunks, embedder.embed([c.text for c in chunks]))
    assert added == 2
    assert duplicates == 1
