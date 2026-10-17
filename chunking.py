import re

# split a log or stack trace into one chunk per exception block
def chunk_log(logs):
    # splits by exception blocks using a regex
    EXCEPTION_REGEX = (
        r"(?m)^.*(?:ERROR|WARN|Exception|Error).*$\n"
        r"(?:^[a-zA-Z0-9_$.]+(?:Exception|Error):?.*$\n)?"
        r"(?:^[ \t]+at .*$\n?|^Caused by:.*$\n?)*"
    )
    p = re.compile(EXCEPTION_REGEX)
    matches = p.findall(logs)
    chunks = []

    for chunk in matches:
        if chunk.strip():
            chunks.append(chunk.strip())

    return chunks

# assumes structured markdown file
# split a runbook into one chunk per heading. Keep each chunk under the model's limit
def chunk_runbook(runbook):
    # split along ## - use a regex for that
    HEADING_REGEX = r"(?m)(?=^#{1,3}\s)"
    p = re.compile(HEADING_REGEX)
    chunks = []
    split_runbook = p.split(runbook)
    for chunk in split_runbook:
        if chunk.strip():
            chunks.append(chunk.strip())

    return chunks

