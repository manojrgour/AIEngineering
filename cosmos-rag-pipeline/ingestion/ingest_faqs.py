import os
from azure.cosmos import CosmosClient, PartitionKey
from openai import AzureOpenAI
from dotenv import load_dotenv
import uuid
from datetime import datetime
import hashlib
from azure.cosmos import exceptions

load_dotenv()
COSMOS_URL = os.getenv("COSMOS_URL")
COSMOS_KEY = os.getenv("COSMOS_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")
OPENAI_DEPLOYMENT = os.getenv("OPENAI_DEPLOYMENT") 

#Cosmos DB setup
cosmos_client = CosmosClient(COSMOS_URL, credential=COSMOS_KEY)
database = cosmos_client.create_database_if_not_exists(id="RAGPipeline")
container = database.create_container_if_not_exists(
    id="faqs",
    partition_key=PartitionKey(path="/type"),
    offer_throughput=1000
)

#Azure OpenAI setup
openai_client = AzureOpenAI(
    api_key=OPENAI_API_KEY,
    api_version="2023-12-01-preview",
    azure_endpoint=OPENAI_ENDPOINT
)

def embed_text(text: str):
    response = openai_client.embeddings.create(
        model=OPENAI_DEPLOYMENT,
        input=text
    )
    
    embedding = response.data[0].embedding
    print(f"Embedding length: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
    return response.data[0].embedding

# Drop the container
#database.delete_container("faqs")

# FAQ List
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

for faq in faqs:
    # Generate embedding from Q+A
    text_for_embedding = faq["question"] + " " + faq["answer"]
    embedding = embed_text(text_for_embedding)
    faq_id = hashlib.md5((faq["question"] + faq["answer"]).encode()).hexdigest()

    doc = {
        "id": faq_id,
        "source": "PetStore_FAQ",
        "type": "faq",
        "question": faq["question"],
        "answer": faq["answer"],
        "tags": ["faq", "petstore"],
        "timestamp": datetime.utcnow().isoformat(),
        "embedding": embedding
    }
    # Insert into Cosmos DB
    #container.upsert_item(doc)
    #print(f"FAQ inserted successfully into Cosmos DB! : {faq['question']}")
    try:
        # Try to read existing doc
        existing = container.read_item(item=faq_id, partition_key="faq")
        # Replace if found
        container.replace_item(item=faq_id, body=doc)
        print(f"FAQ updated: {faq['question']}")
    except exceptions.CosmosResourceNotFoundError:
        # Create if not found
        container.create_item(doc)
        print(f"FAQ inserted: {faq['question']}")

