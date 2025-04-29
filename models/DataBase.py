import yaml
from sqlalchemy import create_engine, MetaData
from pathlib import Path
from contextlib import contextmanager

from enums import DatabaseType as Type


class Engine:
    @staticmethod
    def connect_local(db_path: Path) -> str:
        return f"sqlite:///{db_path}", Type.Local
    
    @staticmethod
    def connect_azure(server: str, database: str, username: str, password: str) -> str:
        return f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server", Type.Azure

import logging

class Database:
    def __init__(self, connection_string: str, db_type: Type):
        self.engine = create_engine(connection_string)
        self.metadata = MetaData()
        self.type = db_type

    @contextmanager
    def switch_on(self):
        """Manage database connection with specific behavior based on type"""
        connection = None
        try:
            if self.type == Type.Azure:
                logging.info("Connecting to Azure SQL database.")
                connection = self.engine.connect()
                yield connection

            elif self.type == Type.Local:
                logging.info("Connecting to local SQLite database.")
                connection = self.engine.connect()
                yield connection

            # Add more conditions for other types if needed

        finally:
            if connection:
                connection.close()
            self.engine.dispose()
    
    def build(self):
        """Just creates the database if it doesn't exist"""
        if not self.engine:
            raise ValueError("Database not connected")
        with self.engine.connect() as conn:
            pass
    
