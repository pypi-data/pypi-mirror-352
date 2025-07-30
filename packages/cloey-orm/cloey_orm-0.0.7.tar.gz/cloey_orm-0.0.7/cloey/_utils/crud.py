from .logger import log_sql

def get_placeholder():
    return '%s'

def create_helper(conn, tn, data):
    placeholders = ", ".join(f"{get_placeholder()}" for _ in data.values())

    columns = ", ".join(data.keys())
    values = tuple(data.values())

    sql = f"INSERT INTO {tn} ({columns}) VALUES ({placeholders}) RETURNING *"

    log_sql(sql, values)

    # Execute the query
    cursor = conn.execute_query(sql, values, True)
    row = cursor.fetchone()
    return dict(zip([column[0] for column in cursor.description], row))

def find_helper(conn, tn, criteria):
    """Find one record in a table given a criteria dict."""
    if not criteria:
        raise ValueError("Criteria for lookup cannot be empty.")

    condition = " AND ".join(f"{key}={get_placeholder()}" for key in criteria.keys())
    values = tuple(criteria.values())

    sql = f"SELECT * FROM {tn} WHERE {condition}"

    log_sql(sql, values)
    cursor = conn.execute_query(sql, values)
    rows = cursor.fetchall()
    return [dict(zip([column[0] for column in cursor.description], row)) for row in rows]


def find_one_helper(conn, tn, criteria):
    """Find one record in a table given a criteria dict."""
    if not criteria:
        raise ValueError("Criteria for lookup cannot be empty.")

    condition = " AND ".join(f"{key}={get_placeholder()}" for key in criteria.keys())
    values = tuple(criteria.values())

    sql = f"SELECT * FROM {tn} WHERE {condition}"

    log_sql(sql, values)
    cursor = conn.execute_query(sql, values)
    row = cursor.fetchone()
    if not row:
        return None
    return dict(zip([column[0] for column in cursor.description], row))

def find_all_helper(conn, tn):
    sql = f"SELECT * FROM {tn}"
    log_sql(sql, ())  # Log the query
    cursor = conn.execute_query(sql)
    rows = cursor.fetchall()
    return [dict(zip([column[0] for column in cursor.description], row)) for row in rows]

def update_helper(conn, tn, data, criteria):
    if not criteria:
        raise ValueError("Criteria for lookup cannot be empty.")
    
    exist = find_one_helper(conn, tn, criteria)
    if not exist:
        return None
    
    update_fields = ", ".join(f"{key}={get_placeholder()}" for key in data.keys())
    condition = " AND ".join(f"{key}={get_placeholder()}" for key in criteria.keys())
    values = tuple(data.values()) + tuple(criteria.values())
    sql = f"UPDATE {tn} SET {update_fields} WHERE {condition} RETURNING *"
    log_sql(sql, values)
    cursor = conn.execute_query(sql, values, commit=True)
    row = cursor.fetchone()
    if not row:
        return None
    
    return dict(zip([column[0] for column in cursor.description], row))

def delete_helper(conn, tn, criteria):
    """Delete records based on a criteria dict."""
    if not criteria:
        raise ValueError("Criteria for lookup cannot be empty.")
    
    exist = find_one_helper(conn, tn, criteria)
    if not exist:
        return False
    
    condition = " AND ".join(f"{key}={get_placeholder()}" for key in criteria.keys())
    values = tuple(criteria.values())

    sql = f"DELETE FROM {tn} WHERE {condition}"
    log_sql(sql, values)
    conn.execute_query(sql, values, commit=True)
    return True