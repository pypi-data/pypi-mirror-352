import os
from datetime import datetime
from cloey._constants import LOG_FILE

def log_sql(query: str, params: tuple):
    """Log the SQL query with parameters."""
    log_dir = os.path.dirname(LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    with open(LOG_FILE, 'a') as log_file:
        log_file.write(f"{datetime.now()} - Executing SQL: {query} | Parameters: {params}\n")