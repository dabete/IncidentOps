import psycopg
import pytest
from ingest import ingest  # assumes your function is in ingest.py

DB_URL = "postgresql://postgres:dev@localhost:5433/postgres"


@pytest.fixture(autouse=True)
def clean_db():
    """Runs before each test to give a clean items table."""
    with psycopg.connect(DB_URL, autocommit=True) as conn:
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
    yield


def test_ingest_log(tmp_path):
    # 1. Create a dummy log file with numbers and an IP to test sanitization
    log_content = (
        "2026-10-17 12:00:00 ERROR NullPointerException at service 192.168.1.1:8080\n"
        "java.lang.NullPointerException: object is null\n"
        "\tat com.example.App.run(App.java:42)\n"
    )
    log_file = tmp_path / "app_error.log"
    log_file.write_text(log_content, encoding="utf-8")

    # 2. Run ingest
    ingest(str(log_file))

    # 3. Verify row in Postgres
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT source, chunk_text FROM items;")
            rows = cur.fetchall()

            # Confirm at least one chunk inserted
            assert len(rows) > 0

            # Confirm path was saved
            assert rows[0][0] == str(log_file)

            # Confirm sanitization worked (<TIMESTAMP> and <IP> replaced)
            chunk_text = rows[0][1]
            assert "<TIMESTAMP>" in chunk_text
            assert "<IP>" in chunk_text
            assert "192.168.1.1" not in chunk_text


def test_ingest_runbook(tmp_path):
    # 1. Create a markdown runbook with two headings
    runbook_content = (
        "# Database Failover\n"
        "Follow these steps to recover the replica.\n\n"
        "## Step 1: Promote Replica\n"
        "Run the promote command on node-02.\n"
    )
    md_file = tmp_path / "db_runbook.md"
    md_file.write_text(runbook_content, encoding="utf-8")

    # 2. Run ingest
    ingest(str(md_file))

    # 3. Verify rows in Postgres
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT chunk_text FROM items;")
            rows = cur.fetchall()

            # Should have chunks corresponding to headings
            assert len(rows) >= 1
            # Runbooks should not have been sanitized with log tokens
            assert "<TIMESTAMP>" not in rows[0][0]