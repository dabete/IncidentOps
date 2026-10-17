from sentence_transformers import SentenceTransformer
from pgvector import Vector
from pgvector.psycopg import register_vector
import psycopg
import numpy as np
from numpy.linalg import norm

# connect to the postgres docker container
conn = psycopg.connect(
    "postgresql://postgres:dev@localhost:5433/postgres",
    autocommit=True,
)

# enable the extension in Postgres
conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")

# register the pgvector type adapter with this connection
register_vector(conn)

conn.execute("DROP TABLE IF EXISTS items;")
conn.execute("""
            CREATE TABLE items (
                id bigserial PRIMARY KEY,
                source VARCHAR(256) NOT NULL,
                service VARCHAR(100) NOT NULL,
                chunk_text TEXT NOT NULL,
                embedding vector(384) NOT NULL,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );
        """)

#insert vectors
# conn.execute("INSERT INTO items (embedding) VALUES (%s)", 
#             (Vector([1.0, 2.0, 3.0]),)
#             )

# conn.execute("INSERT INTO items (embedding) VALUES (%s)", 
#             (Vector([4.0, 5.0, 6.0]),)
#             )

# count = conn.execute("SELECT count(*) FROM items;").fetchone()[0]
# print(f"Total rows in items table: {count}")

# embedding = Vector([1,2,3])
# # get nearest neighbours to a vector
# results = conn.execute("SELECT * FROM items ORDER BY embedding <-> %s LIMIT 5", (embedding,)).fetchall()
# print(results)


model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

sentences = [
    "The weather is lovely today.",
    "It's so sunny outside!",
    "He drove to the stadium.",
    "He went to the stadium",
    "He watched football",
    "The weather is shit today",
    "It is raining",
    "There is a thunderstorm",
]

embeddings = model.encode(sentences)

query = "I am on my way to watch football"
B = model.encode(query)

# do cosine similarity search with numpy
cosine = np.dot(embeddings, B) / (norm(embeddings, axis=1) * norm(B))
print("Numpy cosine similarity = ", cosine)




#print(embeddings.shape)

# similarities = model.similarity(embeddings, embeddings)
# print(similarities)