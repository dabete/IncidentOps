from chunking import chunk_log, chunk_runbook
from sanitize import sanitize_log
from sentence_transformers import SentenceTransformer
from pgvector import Vector
from pgvector.psycopg import register_vector
import psycopg

# file -> sanitize -> chunk -> embed -> insert
def ingest(path):
    log = False
    # runbooks ends in .md
    # logs are either .log or .txt
    with open(path, "r", encoding="utf-8") as file:
        text = file.read()

    if path.endswith(".log") or path.endswith(".txt"):
        log = True

    # chunk
    if log:
        chunks = chunk_log(text)
    else:
        chunks = chunk_runbook(text)

     # sanitize - if a log
    if log:
        chunks = [sanitize_log(chunk) for chunk in chunks]

    # embed
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embeddings = model.encode(chunks).tolist()

    # insert
    # connect to the postgres docker container
    with psycopg.connect(
    "postgresql://postgres:dev@localhost:5433/postgres",
    autocommit=True,
    ) as conn:

        with conn.cursor() as cur:
        
            # enable the extension in Postgres
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            # register the pgvector type adapter with this connection
            register_vector(conn)

            
            cur.execute("""
                    CREATE TABLE IF NOT EXISTS items (
                        id bigserial PRIMARY KEY,
                        source VARCHAR(256) NOT NULL,
                        service VARCHAR(100) NOT NULL,
                        chunk_text TEXT NOT NULL,
                        embedding vector(384) NOT NULL,
                        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                    );
                """)

            # join together corresponding chunks and embeddings
            rows = [
                (path, "my-service", chunk, emb)
                for chunk, emb in zip(chunks, embeddings)
            ]

            # executemany as looping over the embeddings and using a cursor for all
            # of them is slow
            cur.executemany(
                """
                INSERT INTO items (source, service, chunk_text, embedding)
                VALUES (%s, %s, %s, %s);
                """,
                rows,
            )

        



