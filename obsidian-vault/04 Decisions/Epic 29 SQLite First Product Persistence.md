# Decision - SQLite-first Product Persistence

SQLite is the default transactional database for the first product delivery.
It reduces operational setup while the product resource model stabilizes.
SQLAlchemy models remain portable so PostgreSQL can replace SQLite later.

Qdrant remains exclusively responsible for embeddings, chunks, corpus
documents, and retrieval metadata.
