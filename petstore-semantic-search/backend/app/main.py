from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from .models import Product, Customer, FAQ
from .seed_data import seed
from qdrant_client import QdrantClient
from .rag_pipeline import build_index, semantic_search
from .models import Product, FAQ
from sentence_transformers import SentenceTransformer

app = FastAPI()
# Qdrant client
qdrant = QdrantClient(url="http://qdrant:6333")
model = SentenceTransformer("all-MiniLM-L6-v2")

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    seed()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/products")
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@app.get("/customers/{customer_id}")
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    return db.query(Customer).filter(Customer.id == customer_id).first()

@app.get("/faqs")
def list_faqs(db: Session = Depends(get_db)):
    return db.query(FAQ).all()

@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    products = db.query(Product).all()
    faqs = db.query(FAQ).all()
    build_index(products, faqs)
    db.close()

@app.get("/search/")
def search(query: str):
    results = semantic_search(query)
    return [{"id": r.id, "name": r.name, "price": r.price} for r in results]

@app.get("/semantic-search")
def semantic_search(q: str = Query(..., description="Search query"), limit: int = 3):
    db: Session = SessionLocal()

    # Encode query
    vector = model.encode(q).tolist()

    # Search Qdrant
    results = qdrant.query_points(
        collection_name="petstore",
        query=vector,
        limit=limit
    ).points

    # Hydrate results from Postgres
    hydrated = []
    for hit in results:
        payload = hit.payload
        print(hit.payload, "score:", hit.score)
        if payload["type"] == "product":
            product = db.query(Product).filter(Product.id == payload["product_id"]).first()
            if product:
                hydrated.append({
                    "id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "description": product.description,
                    "price": product.price,
                    "discount": product.discount,
                    "stock": product.stock,
                    "score": hit.score
                })
        elif payload["type"] == "faq":
            faq = db.query(FAQ).filter(FAQ.id == payload["faq_id"]).first()
            if faq:
                hydrated.append({
                    "id": faq.id,
                    "question": faq.question,
                    "answer": faq.answer,
                    "score": hit.score
                })

    db.close()
    return {"query": q, "results": hydrated}
