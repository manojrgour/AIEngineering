import os
from azure.cosmos import CosmosClient
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load secrets
load_dotenv()
COSMOS_URL = os.getenv("COSMOS_URL")
COSMOS_KEY = os.getenv("COSMOS_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")
OPENAI_DEPLOYMENT = os.getenv("OPENAI_DEPLOYMENT")  # e.g., "text-embedding-ada-002"

# Cosmos DB setup
cosmos_client = CosmosClient(COSMOS_URL, credential=COSMOS_KEY)
database = cosmos_client.get_database_client("RAGPipeline")
container = database.get_container_client("faqs")

# Azure OpenAI setup
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
    return response.data[0].embedding

def query_faqs(user_query: str, top_k: int = 3):
    # Embed the user query
    query_embedding = embed_text(user_query)

    # Cosmos DB vector search query
    results = container.query_items(
        query="""
        SELECT TOP @top_k c.id, c.question, c.answer, c.source, c.tags
        FROM c
        ORDER BY VectorDistance(c.embedding, @embedding)
        """,
        parameters=[
            {"name": "@top_k", "value": top_k},
            {"name": "@embedding", "value": query_embedding}
        ],
        enable_cross_partition_query=True
    )

    return list(results)

if __name__ == "__main__":
    user_query = "How long is shipping?"
    faqs = query_faqs(user_query, top_k=2)
    for faq in faqs:
        print(f"Q: {faq['question']}")
        print(f"A: {faq['answer']}")
        print("---")