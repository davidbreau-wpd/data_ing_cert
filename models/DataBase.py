import logging
from pathlib import Path 
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from typing import Final
from sqlmodel import SQLModel, Session

from enums import DatabaseType as Type
from .tables import IngestionTracking, ServiceReportMetadata, ServiceReportChecklist


class Engine:
    def __init__(self, local_connection: Path | None = None, azure_connection: dict | None = None):
        if local_connection is not None and azure_connection is not None:
            raise ValueError("Cannot specify both local and azure connections")
        if local_connection is None and azure_connection is None:
            raise ValueError("Must specify either local or azure connection")

        if local_connection:
            self.type = Type.Local
            self.connection_string = f"sqlite:///{local_connection}"
        elif azure_connection:
            self.type = Type.Azure
            self.connection_string = f"mssql+pyodbc://{azure_connection['username']}:{azure_connection['password']}@{azure_connection['server']}/{azure_connection['database']}?driver=ODBC+Driver+17+for+SQL+Server"
        else:
            raise ValueError("Either local_connection or azure_connection must be provided")


class Database:
    def __init__(self):
        self.engine = None

    @contextmanager
    def switch_on(self, engine_config: Engine):
        """Manage database connection with specific behavior based on type"""
        self.engine = create_engine(engine_config.connection_string)
        SQLModel.metadata.create_all(self.engine)
        try:
            logging.info(f"Connecting to {engine_config.type.name} database.")
            yield self
        finally:
            if self.engine:
                self.engine.dispose()

    def build(self) -> None:
        """Creates the database and tables if they don't exist"""
        if not self.engine:
            raise ValueError("Database not connected")
        SQLModel.metadata.create_all(self.engine)
        logging.info("✅ Database built")

    def drop_tables(self) -> None:
        """Drops all tables after confirmation"""
        confirm = input("\n⚠️ Are you sure you want to drop all tables? (y/N): ")
        if confirm.lower() != 'y':
            raise Exception("❌ Operation cancelled by user")
            
        SQLModel.metadata.drop_all(self.engine)
        logging.info("✅ All tables dropped")
    
    def dump(self) -> None:
        """Delete the database and close all connections"""
        confirm = input("\n⚠️ Are you sure you want to delete the database? (y/N): ")
        if confirm.lower() != 'y':
            raise Exception("❌ Operation cancelled by user")
            
        self.drop_tables()
        if self.engine:
            self.engine.dispose()
        logging.info("✅ Database deleted")


# Constants
LOCAL_DB_FOLDER: Final[Path] = Path('data')
LOCAL_DB_NAME: Final[str] = 'windmanager_test.db'
LOCAL_DB_PATH: Final[Path] = LOCAL_DB_FOLDER / LOCAL_DB_NAME


class LocalDatabase(Database):
    @classmethod
    def connect(cls):
        """Returns a context manager for the local test database"""
        return cls().switch_on(Engine(local_connection=LOCAL_DB_PATH))