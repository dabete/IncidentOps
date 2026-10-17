import psycopg
import pytest
from pgvector.psycopg import register_vector
from search import model, search

DB_URL = "postgresql://postgres:dev@localhost:5433/postgres"


@pytest.fixture(autouse=True)
def setup_items_table():
    """Seeds the items table with two distinct chunks for testing."""
    with psycopg.connect(DB_URL, autocommit=True) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute("DROP TABLE IF EXISTS items;")
            cur.execute(
                """
                CREATE TABLE items (
                    id bigserial PRIMARY KEY,
                    source VARCHAR(256) NOT NULL,
                    service VARCHAR(100) NOT NULL,
                    chunk_text TEXT NOT NULL,
                    embedding vector(384) NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                );
            """
            )

            # Insert two clearly distinct chunks
            text_1 = (
                "Database connection failed: timeout connecting to PostgreSQL"
            )
            text_2 = (
                "Runbook: how to clean up disk space when /var partition is full"
            )

            emb_1 = model.encode(text_1).tolist()
            emb_2 = model.encode(text_2).tolist()

            cur.executemany(
                """
                INSERT INTO items (source, service, chunk_text, embedding)
                VALUES (%s, %s, %s, %s);
                """,
                [
                    ("db.log", "postgres-service", text_1, emb_1),
                    ("disk.md", "ops-service", text_2, emb_2),
                ],
            )
    yield


def test_search_returns_most_relevant_chunk():
    # Query clearly related to database connection issues
    query = "ERROR: connection timed out to database host"

    results = search(query, k=1)

    # 1. Ensure at least one result came back
    assert len(results) == 1

    # 2. Check the returned tuple: (id, source, service, chunk_text)
    # The top result must be the database chunk, not the disk cleanup chunk
    top_chunk_text = results[0][3]
    assert "Database connection failed" in top_chunk_text
    assert "disk space" not in top_chunk_text