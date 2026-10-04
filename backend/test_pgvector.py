from app.services.embedding_service import create_embeddings
from app.services.similarity_search import search_with_pgvector

document_id = input("Enter your uploaded document ID: ")
question = input("Enter a question about your PDF: ")

query_embedding = create_embeddings([question])[0]

results = search_with_pgvector(
    query_embedding,
    document_id,
    top_k=3
)

for result in results:
    print("\nPage:", result["page"])
    print("Similarity:", result["score"])
    print("Text:", result["text"][:300])
