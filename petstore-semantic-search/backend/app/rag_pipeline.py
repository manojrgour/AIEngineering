from sentence_transformers import SentenceTransformer
from .vector_store import VectorStore
from .models import Product, FAQ

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")
product_store = VectorStore(dim=384)
faq_store = VectorStore(dim=384)

def build_index(products, faqs):
    product_texts = [p.name for p in products]
    embeddings = model.encode(product_texts)
    product_store.add(embeddings, products)

    faq_texts = [f.question for f in faqs]
    faq_embeddings = model.encode(faq_texts)
    faq_store.add(faq_embeddings, faqs)

def semantic_search(query: str, k=2):
    query_embedding = model.encode([query])[0]
    product_results = product_store.search(query_embedding, k)
    faq_results = faq_store.search(query_embedding, k)

    return {
        "products": [{"id": p.id, "name": p.name, "price": p.price} for p in product_results],
        "faqs": [{"id": f.id, "question": f.question, "answer": f.answer} for f in faq_results],
    }
