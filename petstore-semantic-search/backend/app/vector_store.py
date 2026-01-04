import faiss
import numpy as np

class VectorStore:
    def __init__(self, dim=384):
        self.index = faiss.IndexFlatL2(dim)
        self.metadata = []

    def add(self, embeddings, items):
        self.index.add(np.array(embeddings).astype("float32"))
        self.metadata.extend(items)

    def search(self, query_embedding, k=5):
        D, I = self.index.search(np.array([query_embedding]).astype("float32"), k)
        return [self.metadata[i] for i in I[0]]