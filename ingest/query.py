"""Ask the index a question: python -m ingest.query "your question" """
import sys

from .embedder import Embedder
from .indexer import Indexer


def search(question: str, collection_name: str = "my-docs",
           persist_dir: str = "./chroma_db", k: int = 3) -> list[dict]:
    embedder = Embedder()
    indexer = Indexer(persist_dir=persist_dir)
    collection = indexer.get_collection(collection_name)
    q_emb = embedder.embed([question])[0]
    results = collection.query(query_embeddings=[q_emb], n_results=k)
    hits = []
    for doc, meta, dist in zip(results["documents"][0],
                               results["metadatas"][0],
                               results["distances"][0]):
        hits.append({"text": doc, "source": meta["source"],
                     "page": meta["page"], "distance": dist})
    return hits


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "What is retrieval augmented generation?"
    for hit in search(question):
        print(f"\n[{hit['source']} p.{hit['page']} | distance {hit['distance']:.3f}]")
        print(hit["text"][:300].replace("\n", " "))
