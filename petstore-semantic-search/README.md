# 🐾 PetStore Semantic Search

Semantic search demo using **FastAPI**, **Postgres**, and **Qdrant**.  
This project showcases how to combine **vector search** with **relational data hydration** for a realistic e‑commerce use case.

---

## 🚀 Features
- **Semantic Search Endpoint**: `/semantic-search?q=...`
- **Vector Database (Qdrant)**: Stores embeddings for products and FAQs
- **Relational Database (Postgres)**: Holds structured product, customer, and FAQ data
- **Hydration Logic**: Matches semantic hits with full product/FAQ details from Postgres
- **Containerized Deployment**: FastAPI, Postgres, and Qdrant orchestrated via Docker Compose
- **Seeding Script**: Automatically populates products and FAQs with embeddings

---

## 🛠️ Tech Stack
- **FastAPI** – lightweight Python web framework  
- **SQLAlchemy** – ORM for Postgres  
- **Qdrant** – vector database for semantic search  
- **Sentence Transformers** – embedding model (`all-MiniLM-L6-v2`)  
- **Docker Compose** – service orchestration  

---

## 📂 Project Structure

## ⚡ Getting Started

1. Clone the repo
```bash
git clone https://github.com/manojrgour/AIEngineering.git
cd AIEngineering/petstore-semantic-search


2. Build and run
docker-compose up --build


3. Seed data
The seed_data.py script runs automatically when the container starts, populating Postgres and Qdrant.

🔍 Example Query
curl "http://localhost:8000/semantic-search?q=Cat Toys"


Sample Response
{
  "query": "Cat Toys",
  "results": [
    {
      "id": 2,
      "name": "Cat Toy Mouse",
      "category": "Cat Toys",
      "description": "Interactive toy for cats",
      "price": 9.99,
      "discount": 0.05,
      "stock": 200,
      "score": 0.87
    }
  ]
}




