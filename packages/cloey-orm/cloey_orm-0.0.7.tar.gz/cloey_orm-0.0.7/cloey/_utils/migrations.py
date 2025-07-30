from typing import Dict, List

def gen_alter_statements_helper(tn: str, o_schema: Dict[str, str], n_schema: Dict[str, str]) -> List[str]:
    """Generate ALTER TABLE statements to migrate from old_schema to new_schema."""
    alter_statements = []

    # Detect added columns
    for column in n_schema:
        if column not in o_schema:
            alter_statements.append(
                f"ALTER TABLE {tn} ADD COLUMN IF NOT EXISTS {column} {n_schema[column]};"
            )

    # Detect removed columns
    for column in o_schema:
        if column not in n_schema:
            alter_statements.append(
                f"-- WARNING: Column {column} was removed. You need to recreate the table to remove columns."
            )

    return alter_statements
