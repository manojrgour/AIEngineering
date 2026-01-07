import os
import time
import statistics
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

# --- Setup ---
load_dotenv()
url = os.getenv("COSMOS_URL")
key = os.getenv("COSMOS_KEY")
database_name = "RAGPipeline"
container_name = "faqs"

client = CosmosClient(url, key)
database = client.get_database_client(database_name)
container = database.get_container_client(container_name)

# --- Test Embedding ---
# Replace with a real embedding vector (list of floats)
test_embedding = [0.1] * 10   # Example: 10-dim vector

# --- Benchmark Function ---
def benchmark(vector_path, top_n=3, runs=20):
    latencies = []
    for i in range(runs):
        query = f"""
        SELECT TOP {top_n} c.id, c.question, c.answer
        FROM c
        ORDER BY VectorDistance(c.{vector_path}, @embedding)
        """
        start = time.time()
        results = list(container.query_items(
            query=query,
            parameters=[{"name": "@embedding", "value": test_embedding}],
            enable_cross_partition_query=True
        ))
        end = time.time()
        latencies.append(end - start)
    print(f"--- Benchmark: {vector_path}, TOP {top_n}, Runs {runs} ---")
    print(f"Avg Latency: {statistics.mean(latencies):.4f}s")
    print(f"Min Latency: {min(latencies):.4f}s")
    print(f"Max Latency: {max(latencies):.4f}s")
    print(f"Std Dev: {statistics.stdev(latencies):.4f}s")
    print()

# --- Run Benchmarks ---
for path in ["contentVector", "coverImageVector"]:
    for top_n in [3, 10, 50]:
        benchmark(path, top_n=top_n, runs=20)