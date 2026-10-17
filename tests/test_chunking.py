import pytest
from chunking import chunk_log, chunk_runbook


# ==========================================
# 1. Tests for chunk_log
# ==========================================

def test_chunk_log_extracts_multiline_stack_trace():
    """Verify that normal INFO lines are dropped and the full exception trace is extracted."""
    log_sample = (
        "17/06/09 20:10:40 INFO TaskSetManager: Starting task 0.0 in stage 1.0\n"
        "17/06/09 20:10:41 ERROR Executor: Exception in task 0.0 in stage 1.0 (TID 12)\n"
        "java.lang.NullPointerException: Value is null\n"
        "    at org.apache.spark.TaskRunner.run(TaskRunner.scala:42)\n"
        "    at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1142)\n"
        "17/06/09 20:10:42 INFO TaskSetManager: Finished task 1.0 in stage 1.0\n"
    )

    chunks = chunk_log(log_sample)

    assert len(chunks) == 1
    assert "ERROR Executor: Exception in task 0.0" in chunks[0]
    assert "java.lang.NullPointerException" in chunks[0]
    assert "ThreadPoolExecutor.runWorker" in chunks[0]
    assert "INFO TaskSetManager" not in chunks[0]


def test_chunk_log_captures_caused_by_chains():
    """Verify that root-cause chains ('Caused by:') are retained in the same chunk."""
    log_sample = (
        "17/06/09 20:11:00 ERROR BlockManager: Failed to fetch remote block\n"
        "java.io.IOException: Connection reset by peer\n"
        "    at java.net.SocketInputStream.read(SocketInputStream.java:152)\n"
        "Caused by: java.net.ConnectException: Connection refused\n"
        "    at sun.nio.ch.SocketChannelImpl.checkConnect(Native Method)\n"
    )

    chunks = chunk_log(log_sample)

    assert len(chunks) == 1
    assert "Caused by: java.net.ConnectException" in chunks[0]
    assert "Connection reset by peer" in chunks[0]


def test_chunk_log_returns_empty_when_no_errors():
    """Verify that pure operational logs yield zero chunks."""
    log_sample = (
        "17/06/09 20:10:40 INFO App: Initializing\n"
        "17/06/09 20:10:41 INFO App: Ready to receive traffic\n"
    )

    assert chunk_log(log_sample) == []


# ==========================================
# 2. Tests for chunk_runbook
# ==========================================

def test_chunk_runbook_splits_and_retains_headings():
    """Verify that chunks split cleanly along headings while retaining the heading text."""
    runbook_sample = (
        "# Spark Remediation Playbook\n"
        "General troubleshooting procedures for executor nodes.\n\n"
        "## Connection Timeout\n"
        "Check firewall settings on port 50010. If closed, restart the security group.\n\n"
        "## Out Of Memory Error\n"
        "Increase executor memory using --executor-memory 4g."
    )

    chunks = chunk_runbook(runbook_sample)

    assert len(chunks) == 3
    # Chunk 0 has the main doc header and overview
    assert chunks[0].startswith("# Spark Remediation Playbook")
    assert "General troubleshooting" in chunks[0]
    # Chunk 1 has the first error section with its heading intact
    assert chunks[1].startswith("## Connection Timeout")
    assert "Check firewall settings" in chunks[1]
    # Chunk 2 has the second error section with its heading intact
    assert chunks[2].startswith("## Out Of Memory Error")
    assert "--executor-memory 4g" in chunks[2]


def test_chunk_runbook_handles_empty_or_whitespace_input():
    """Verify that empty inputs do not produce phantom empty chunks."""
    assert chunk_runbook("") == []
    assert chunk_runbook("   \n\n  \t  ") == []