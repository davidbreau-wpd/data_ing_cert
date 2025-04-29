import yaml
from sqlalchemy import create_engine, MetaData
from pathlib import Path
from contextlib import contextmanager

from enums import DatabaseType as Type


class Engine:
    @staticmethod
    def connect_local(db_path: Path) -> str:
        return f"sqlite:///{db_path}"
    
    @staticmethod
    def connect_azure(server: str, database: str, username: str, password: str) -> str:
        return f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"

class Database:
    def __init__(self):
        self.engine = None
        self.metadata = MetaData()
    
    @contextmanager
    def switch_on(self, connection_string: str):
        """Initialize and manage database connection"""
        try:
            self.engine = create_engine(connection_string)
            connection = self.engine.connect()
            yield connection
        finally:
            if connection:
                connection.close()
            if self.engine:
                self.engine.dispose()
    
    def build(self):
        """Just creates the database if it doesn't exist"""
        if not self.engine:
            raise ValueError("Database not connected")
        with self.engine.connect() as conn:
            pass
    
