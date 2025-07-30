import os
from datetime import datetime
from typing import TypeVar, Dict, Any, List, Optional, get_origin, get_args

from cloey.connection import BaseDBConnection
from cloey.database import SQLiteConnection

from cloey._utils import *
from cloey._constants import MIGRATIONS_DIR

T = TypeVar('T', bound='BaseModel')

# Global connection manager
# db_connection: BaseDBConnection = SQLiteConnection("default.db")  # Default to SQLite


class BaseModel:
    __tablename__: str
    __initialized_tables = set()

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def _ensure_table(cls):
        if cls.__name__ not in cls.__initialized_tables:
            cls.create_table()
            cls.__initialized_tables.add(cls.__name__)

    @classmethod
    def _get_conn_type(cls):
        """"Get the database connection type"""
        
        return cls.get_connection().__class__.__module__ 

    @classmethod
    def _get_table_name(cls):
        """Get the table name"""

        if getattr(cls, '__tablename__', None) is not None:
            return f'"{cls.__tablename__}"' if cls._get_conn_type() == 'psycopg2.extensions' else f'{cls.__tablename__}'

        cls.__tablename__ = f'{cls.__name__.lower()}s'
        return f'"{cls.__tablename__}"' if cls._get_conn_type() == 'psycopg2.extensions' else f'{cls.__tablename__}'
    
    @classmethod
    def __get_placeholder(cls):
        """Get placeholder based on database connection type"""
        
        conn_type = cls._get_conn_type()
        if conn_type == 'psycopg2.extensions':
            return '%s' 
        elif conn_type == 'sqlite3':
            return '?'
        else:
            raise ValueError("Unsupported database connection type")

    @classmethod
    def set_connection(cls, connection: BaseDBConnection):
        """Set the database connection."""
        global db_connection
        db_connection = connection
        db_connection.connect()
    

    @classmethod
    def get_connection(cls) -> any:
        """Get the current database connection."""
        return db_connection.get_connection()

    @classmethod
    def create_table(cls):
        """Create the table in the database."""
       
        table_name = cls._get_table_name()

        if cls._get_conn_type() == 'sqlite3':
            _default_columns = [
                "id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL",
                "created_at TEXT DEFAULT (datetime('now'))"
            ]

        elif cls._get_conn_type() == 'psycopg2.extensions':
            _default_columns: List[str] = [
                "id SERIAL PRIMARY KEY NOT NULL",
                "uuid UUID UNIQUE DEFAULT gen_random_uuid()",
                "created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP"
            ]

        else:
            raise ValueError("Unsupported database connection type")

        # Generate the rest of the columns
        columns = [*_default_columns, *cls._get_columns()]
        columns_sql = ", ".join(columns)

        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"
        
        log_sql(sql, ())
        db_connection.execute_query(sql, commit=True)

    @classmethod
    def _get_columns(cls) -> List[str]:
        """Get the SQL column definitions for the model."""
        columns = []
        for key, annotation in cls.__annotations__.items():
            if key == "id":
                continue
            column_type = "TEXT"
            origin = get_origin(annotation)
            args = get_args(annotation)

            if annotation == int:
                column_type = "INTEGER"
            elif annotation == bool:
                column_type = "BOOLEAN"
            elif annotation == float:
                column_type = "REAL"
            elif isinstance(annotation, type) and issubclass(annotation, BaseModel):
                ref_table = annotation._get_table_name()
                _column = foreign_key_helper(ref_table, key)
                columns.append(_column)
                def make_property(related_cls, rel_key):
                    def getter(self):
                        return related_cls.filter(**{f"{rel_key}_id": self.id})
                    return property(getter)
                def get_property(_cls, _key):
                    def getter(self):
                        return _cls.get(id=getattr(self, f'{_key}_id'))
                    return property(getter)
                print(annotation, cls.__tablename__, key, cls) 
                setattr(annotation, cls.__tablename__, make_property(cls, key))
                setattr(cls, key, get_property(annotation, key))
                continue
            else:
                pass

            if origin is list or not args:
                columns.append(f"{key} {column_type}")
        return columns

    @classmethod
    def create(cls, **data):
        """Insert a new record into the table."""
        cls._ensure_table()
        row = create_helper(db_connection, cls._get_table_name(), data)
        return cls(**row) 
        
    @classmethod
    def filter(cls, **kwargs) -> List[T]:
        """Find a record by given criteria."""
        cls._ensure_table()
        table_name = cls._get_table_name()

        rows = find_helper(conn=db_connection, tn=table_name, criteria=kwargs)
        return [cls(**row) for row in rows]
    
    @classmethod
    def get(cls, **kwargs) -> Optional[T]:
        """Find a record by given criteria."""
        cls._ensure_table()
        table_name = cls._get_table_name()

        row = find_one_helper(conn=db_connection, tn=table_name, criteria=kwargs)
        if not row:
            return None
        return cls(**row)

    @classmethod
    def all(cls) -> List[T]:
        """Get all records from the table."""
        cls._ensure_table()
        rows = find_all_helper(db_connection, cls._get_table_name())
        return [cls(**row) for row in rows]

    @classmethod
    def update(cls, data: Dict[str, Any], **conditions):
        """Update records based on conditions."""
        cls._ensure_table()
        updated = update_helper(db_connection, cls._get_table_name(), data, conditions)
        if not updated:
            return None
        return cls(**updated)

    @classmethod
    def delete(cls, **conditions):
        """Delete records based on conditions."""
        cls._ensure_table()
        return delete_helper(db_connection, cls._get_table_name(), conditions)


    @classmethod
    def get_current_schema(cls) -> Dict[str, str]:
        """Get the current schema of the table."""
        sql = """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = %s AND table_schema = 'public';
        """
        table_name = cls._get_table_name()
        cursor = db_connection.execute_query(sql, (table_name,))
        return {row[1]: row[2] for row in cursor.fetchall()}

    @classmethod
    def generate_migration_script(cls, old_schema: Dict[str, str], new_schema: Dict[str, str]) -> str:
        """Generate a migration script to update the table schema."""
        alter_statements = gen_alter_statements_helper(tn=cls._get_table_name(), o_schema=old_schema, n_schema=new_schema)

        return "\n".join(alter_statements)

    @classmethod
    def create_migration_file(cls, sql_commands: str):
        """Create a migration file with SQL commands."""
        cls._ensure_table()
        if not os.path.exists(MIGRATIONS_DIR):
            os.makedirs(MIGRATIONS_DIR)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{MIGRATIONS_DIR}/migration_{cls._get_table_name()}_{timestamp}.sql"

        with open(filename, 'w') as f:
            f.write(sql_commands)
            print(f"Migration script saved: {filename}")

    @classmethod
    def generate_and_save_migration(cls):
        """Generate and save the migration script."""
        old_schema = cls.get_current_schema()
        new_schema = {column.split()[0]: column.split()[1] for column in cls._get_columns()}

        if old_schema == new_schema:
            print("No changes detected, no migration needed.")
            return

        migration_script = cls.generate_migration_script(old_schema, new_schema)
        if migration_script:
            cls.create_migration_file(migration_script)

    @classmethod
    def ensure_migrations_table(cls):
        """Ensure that the migrations table exists."""
        db_connection.execute_query("""
            CREATE TABLE IF NOT EXISTS migrations (
                migration TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """, commit=True)

    @classmethod
    def get_applied_migrations(cls) -> List[str]:
        """Get a list of applied migrations from the database."""
        cls.ensure_migrations_table()  # Ensure the table exists
        cursor = db_connection.execute_query("SELECT migration FROM migrations")
        return [row[0] for row in cursor.fetchall()]

    @classmethod
    def apply_pending_migrations(cls):
        """Apply any migrations that have not been applied yet."""
        cls.ensure_migrations_table()  # Ensure the table exists
        applied_migrations = cls.get_applied_migrations()

        if not os.path.exists(MIGRATIONS_DIR):
            os.makedirs(MIGRATIONS_DIR)

        for migration_file in sorted(os.listdir(MIGRATIONS_DIR)):
            if migration_file not in applied_migrations:
                with open(os.path.join(MIGRATIONS_DIR, migration_file)) as f:
                    sql = f.read()
                    log_sql(sql, ())  # Log the migration script
                    db_connection.execute_query(sql)
                cls.record_migration(migration_file)
                print(f"Applied migration: {migration_file}")

    @classmethod
    def record_migration(cls, migration_name: str):
        """Record the migration in the migrations table."""
        cls.ensure_migrations_table()
        sql = f"INSERT INTO migrations (migration) VALUES ({get_placeholder()})"
        log_sql(sql, (migration_name,))
        db_connection.execute_query(sql, (migration_name,))
