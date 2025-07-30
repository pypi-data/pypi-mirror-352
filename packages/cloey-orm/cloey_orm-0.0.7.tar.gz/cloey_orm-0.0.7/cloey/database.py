import sqlite3
from sqlite3 import Cursor
from typing import Tuple

import psycopg2
from cloey.connection import BaseDBConnection


class SQLiteConnection(BaseDBConnection):

    def __init__(self, database: str):
        self.database = database
        self.conn: sqlite3.Connection = None

    def connect(self) -> None:
        """Establish a connection to the SQLite database."""
        self.conn = sqlite3.connect(self.database)

    def get_connection(self) -> sqlite3.Connection:
        """Get the current SQLite database connection."""
        return self.conn

    def close_connection(self) -> None:
        """Close the SQLite database connection."""
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def execute_query(self, query: str, params: Tuple = (), commit: bool = False) -> Cursor:
        """Execute a SQL query."""
        cursor: Cursor = self.conn.cursor()
        cursor.execute(query, params)
        if commit:
            self.conn.commit()
        return cursor


class PostgreSQLConnection(BaseDBConnection):

    def __init__(self, database: str, user: str, password: str, host: str, port: int):
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn: psycopg2.extensions.connection = None

    def connect(self) -> None:
        """Establish a connection to the PostgreSQL database."""
        self.conn = psycopg2.connect(
            dbname=self.database,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )

    def get_connection(self) -> psycopg2.extensions.connection:
        """Get the current PostgreSQL database connection."""
        return self.conn

    def close_connection(self) -> None:
        """Close the PostgreSQL database connection."""
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def execute_query(self, query: str, params: Tuple = (), commit: bool = False) -> any:
        """Execute a SQL query."""

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        if commit:
            self.conn.commit()

        return cursor
        
