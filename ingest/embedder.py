"""Turn chunk text into embedding vectors (local model, no API key)."""


class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Lazy import: sentence-transformers pulls in torch, so it is only
        # loaded when an Embedder is actually constructed. Importing this
        # module (e.g. in tests that use a fake embedder) stays light.
        from sentence_transformers import SentenceTransformer

        # First run downloads the model (~90 MB) to a local cache.
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(
            texts,
            batch_size=32,
            normalize_embeddings=True,   # cosine similarity behaves correctly
            show_progress_bar=False,
        )
        return vectors.tolist()
