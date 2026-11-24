"""Index chunks into a persistent Chroma collection, dropping duplicates."""
import hashlib


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def chunk_id(source: str, page: int, chunk_index: int, text: str) -> str:
    return f"{source}-p{page}-c{chunk_index}-{content_hash(text)[:12]}"


class Indexer:
    def __init__(self, persist_dir: str = "./chroma_db"):
        # Lazy import: chromadb is heavy, so it is only loaded when an
        # Indexer is actually constructed.
        import chromadb

        self.client = chromadb.PersistentClient(path=persist_dir)

    def get_collection(self, name: str):
        return self.client.get_or_create_collection(
            name=name, metadata={"hnsw:space": "cosine"}
        )

    def add(self, collection, chunks, embeddings) -> tuple[int, int]:
        """Add (chunk, embedding) pairs. Returns (added, duplicates_dropped)."""
        seen: set[str] = set()
        ids, docs, metas, embs = [], [], [], []
        duplicates = 0
        for chunk, emb in zip(chunks, embeddings):
            h = content_hash(chunk.text)
            if h in seen:
                duplicates += 1
                continue
            seen.add(h)
            ids.append(chunk_id(chunk.source, chunk.page, chunk.chunk_index, chunk.text))
            docs.append(chunk.text)
            metas.append({
                "source": chunk.source,
                "page": chunk.page,
                "chunk_index": chunk.chunk_index,
                "content_hash": h,
            })
            embs.append(emb)
        if ids:
            collection.upsert(ids=ids, documents=docs,
                              embeddings=embs, metadatas=metas)
        return len(ids), duplicates
