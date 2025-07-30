from abc import ABC, abstractmethod
from typing import Tuple


class BaseDBConnection(ABC):

    @abstractmethod
    def connect(self) -> None:
        """Establish a connection to the database."""
        pass

    @abstractmethod
    def get_connection(self) -> any:
        """Get the current database connection."""
        pass

    @abstractmethod
    def close_connection(self) -> None:
        """Close the database connection."""
        pass

    @abstractmethod
    def execute_query(self, query: str, params: Tuple = (), commit: bool = False) -> any:
        """Execute a SQL query."""
        pass


