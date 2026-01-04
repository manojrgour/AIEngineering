from .database import Base, engine, SessionLocal
from .models import Product, Customer, Purchase, FAQ

from qdrant_client import QdrantClient
from .rag_pipeline import model

# Initialize Qdrant client
qdrant = QdrantClient(url="http://qdrant:6333")

# Ensure collection exists
qdrant.recreate_collection(
    collection_name="petstore",
    vectors_config={"size": 384, "distance": "Cosine"}  # match your embedding model dimension
)

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Products
    products = [
        {"name": "Grain-Free Dog Food", "category": "Dog Food", "description": "Healthy kibble for dogs", "price": 29.99, "discount": 0.1, "stock": 100},
        {"name": "Cat Toy Mouse", "category": "Cat Toys", "description": "Interactive toy for cats", "price": 9.99, "discount": 0.05, "stock": 200},
        {"name": "Organic Catnip", "category": "Cat Treats", "description": "Premium organic catnip leaves", "price": 5.49, "discount": 0.0, "stock": 150},
        {"name": "Dog Chew Bone", "category": "Dog Toys", "description": "Durable chew bone for dogs", "price": 12.99, "discount": 0.15, "stock": 80},
        {"name": "Pet Shampoo", "category": "Pet Grooming", "description": "Gentle shampoo for sensitive skin", "price": 14.99, "discount": 0.1, "stock": 60},
        {"name": "Cat Scratching Post", "category": "Cat Furniture", "description": "Tall scratching post with sisal rope", "price": 39.99, "discount": 0.2, "stock": 40},
        {"name": "Dog Harness", "category": "Dog Accessories", "description": "Adjustable harness for medium dogs", "price": 24.99, "discount": 0.05, "stock": 70},
        {"name": "Pet Carrier", "category": "Travel", "description": "Airline-approved pet carrier", "price": 49.99, "discount": 0.1, "stock": 30},
        {"name": "Cat Litter Box", "category": "Cat Supplies", "description": "Covered litter box with odor control", "price": 34.99, "discount": 0.0, "stock": 90},
        {"name": "Dog Treats Pack", "category": "Dog Treats", "description": "Mixed flavor dog treats", "price": 19.99, "discount": 0.1, "stock": 120},
        {"name": "Pet Water Fountain", "category": "Pet Supplies", "description": "Automatic water fountain for pets", "price": 59.99, "discount": 0.05, "stock": 25},
        {"name": "Cat Bed", "category": "Cat Furniture", "description": "Soft plush bed for cats", "price": 29.99, "discount": 0.1, "stock": 50},
        {"name": "Dog Raincoat", "category": "Dog Accessories", "description": "Waterproof raincoat for dogs", "price": 22.99, "discount": 0.05, "stock": 40},
        {"name": "Pet Nail Clippers", "category": "Pet Grooming", "description": "Safe nail clippers for pets", "price": 9.99, "discount": 0.0, "stock": 100},
        {"name": "Cat Climbing Tree", "category": "Cat Furniture", "description": "Multi-level climbing tree for cats", "price": 89.99, "discount": 0.15, "stock": 20},
        {"name": "Dog Training Clicker", "category": "Dog Training", "description": "Handheld clicker for training dogs", "price": 4.99, "discount": 0.0, "stock": 200},
        {"name": "Pet Food Storage Bin", "category": "Pet Supplies", "description": "Airtight storage bin for pet food", "price": 44.99, "discount": 0.1, "stock": 35},
        {"name": "Cat Grooming Brush", "category": "Pet Grooming", "description": "Soft bristle brush for cats", "price": 12.99, "discount": 0.05, "stock": 75},
        {"name": "Dog Bed", "category": "Dog Furniture", "description": "Orthopedic bed for large dogs", "price": 79.99, "discount": 0.2, "stock": 15},
        {"name": "Pet Travel Bowl", "category": "Travel", "description": "Collapsible silicone travel bowl", "price": 7.99, "discount": 0.0, "stock": 150},
    ]

    for p in products:
        existing_product = db.query(Product).filter_by(name=p["name"]).first()
        if not existing_product:
            prod = Product(**p)
            db.add(prod)
            db.commit()
            db.refresh(prod)

            add_embeddings_to_qdrant(
                id=prod.id,
                text=f"{prod.name} {prod.description} {prod.category}",
                payload={
                    "type": "product",
                    "product_id": prod.id,
                    "name": prod.name,
                    "category": prod.category
                }
            )
 
    # Customer
    c1 = Customer(name="John", email="john@example.com", preferences="Healthy dog food, eco-friendly toys")
    if not db.query(Customer).first():
        db.add(c1)
    else:
        c1 = db.query(Customer).first()

    # Purchase
    purchase = Purchase(customer=c1, product_id=1)
    db.add(purchase)

    # FAQ
    faqs = [
        {"question": "What is your return policy?", "answer": "You can return items within 30 days of purchase."},
        {"question": "Do you offer bulk discounts?", "answer": "Yes, contact support for details on bulk orders."},
        {"question": "How long does shipping take?", "answer": "Standard shipping takes 3-5 business days."},
        {"question": "Do you ship internationally?", "answer": "Yes, we ship to most countries worldwide."},
        {"question": "Are your products eco-friendly?", "answer": "Many of our products are made from sustainable materials."},
        {"question": "Can I track my order?", "answer": "Yes, tracking information is provided once your order ships."},
        {"question": "Do you sell prescription pet food?", "answer": "Currently we do not offer prescription-only products."},
        {"question": "What payment methods are accepted?", "answer": "We accept credit cards, PayPal, and Apple Pay."},
        {"question": "Is there a loyalty program?", "answer": "Yes, you earn points with every purchase."},
        {"question": "Do you offer same-day delivery?", "answer": "Same-day delivery is available in select cities."},
    ]

    for f in faqs:
        existing_faq = db.query(FAQ).filter_by(question=f["question"]).first()
        if not existing_faq:
            faq = FAQ(**f)
            db.add(faq)
            db.commit()
            db.refresh(faq)

            add_embeddings_to_qdrant(
                id=1000 + faq.id,
                text=f"{faq.question} {faq.answer}",
                payload={
                    "type": "faq",
                    "faq_id": faq.id,
                    "question": faq.question
                }
            )

    db.close()

def add_embeddings_to_qdrant(id: int, text: str, payload: dict):
    # Generate embedding
    vector_embeddings = model.encode(text).tolist()

    # Upsert into Qdrant with payload metadata
    qdrant.upsert(
        collection_name="petstore",
        points=[{
            "id": id,
            "vector": vector_embeddings,
            "payload": payload 
        }]
    )

if __name__ == "__main__":
    seed()
