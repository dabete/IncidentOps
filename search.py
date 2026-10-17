from sanitize import sanitize_log
from sentence_transformers import SentenceTransformer
from pgvector import Vector
from pgvector.psycopg import register_vector
import psycopg

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def search(log, k=3):
    # sanitizes, embeds and queries pgvector
    log = sanitize_log(log)
    
    embedding = model.encode(log).tolist()

    with psycopg.connect(
        "postgresql://postgres:dev@localhost:5433/postgres",
        autocommit=True,
        ) as conn:

        register_vector(conn)

        with conn.cursor() as cur:

            cur.execute("""
                        SELECT id, source, service, chunk_text FROM items ORDER BY embedding <=> %s::vector LIMIT %s;
                        """, 
                        (embedding, k, ))

            results = cur.fetchall()

            return results

            




