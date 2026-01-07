# Cosmos DB Vector Search Benchmarking

This project demonstrates how to benchmark **Azure Cosmos DB vector search** performance using Python.  
It measures query latency and result quality across different vector index configurations.

---

## 🚀 Features
- Create a Cosmos DB container with vector indexes (`flat`, `quantizedFlat`).
- Run queries with `ORDER BY VectorDistance(...)`.
- Benchmark latency for different vector paths, distance functions, and TOP N values.
- Compare trade-offs between accuracy and performance.

---

## 📦 Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/<your-username>/cosmosdb-vector-benchmark.git
   cd cosmosdb-vector-benchmark

2. Install dependencies:
pip install -r requirements.txt   

3. Example requirements.txt:
azure-cosmos>=4.7.0 --pre
numpy

4. Configure environment variables
export COSMOS_URI="https://<your-account>.documents.azure.com:443/"
export COSMOS_KEY="<your-key>"
export COSMOS_DB="<cosmos-db-name>"
export COSMOS_CONTAINER="<cosmos-container>"

5. Run Benchmarks
python benchmark.py

Sample output:
Vector path: contentVector, TOP 3, Latency: 0.1234s, Results: 3
Vector path: coverImageVector, TOP 10, Latency: 0.2567s, Results: 10