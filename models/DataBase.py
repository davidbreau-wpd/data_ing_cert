import logging
from pathlib import Path 
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from typing import Union, List, Final

from enums import DatabaseType as Type


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
        connection = None
        try:
            logging.info(f"Connecting to {engine_config.type.name} database.")
            connection = self.engine.connect()
            yield self
        finally:
            if connection:
                connection.close()
            if self.engine:
                self.engine.dispose()
    
    def execute_sql_files(self, sql_folder: Path, file_pattern: str = "*.sql") -> None:
        """Execute SQL files in the specified folder"""
        if not self.engine:
            raise ValueError("Database not connected")

        with self.engine.connect() as conn:
            for sql_file in sorted(sql_folder.glob(file_pattern)):
                try:
                    with open(sql_file, 'r') as f:
                        sql = f.read()
                    # Using text() to safely parameterize SQL
                    conn.execute(text(sql))
                    conn.commit()
                    logging.info(f"✅ Executed {sql_file.name}")
                except Exception as e:
                    logging.error(f"❌ Error executing {sql_file.name}: {str(e)}")
                    raise

    def build(self) -> None:
        """Creates the database if it doesn't exist"""
        if not self.engine:
            raise ValueError("Database not connected")
        with self.engine.connect() as conn:
            pass

    def drop_tables(self) -> None:
        """Drops all tables after confirmation"""
        confirm = input("\n⚠️ Are you sure you want to drop all tables? (y/N): ")
        if confirm.lower() != 'y':
            raise Exception("❌ Operation cancelled by user")
            
        with self.engine.connect() as conn:
            # Get all tables and drop them
            tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            for table in tables:
                conn.execute(text(f"DROP TABLE IF EXISTS {table[0]}"))
            conn.commit()
        logging.info("✅ All tables dropped")
    
    def delete(self) -> None:
        """Delete the database and close all connections"""
        confirm = input("\n⚠️ Are you sure you want to delete the database? (y/N): ")
        if confirm.lower() != 'y':
            raise Exception("❌ Operation cancelled by user")
            
        self.drop_tables()
        if self.engine:
            self.engine.dispose()
        logging.info("✅ Database deleted")

    def _execute_query(self, query: str, description: str = "") -> None:
        """Execute a single SQL query"""
        if not self.engine:
            raise ValueError("Database not connected")
            
        with self.engine.connect() as conn:
            try:
                conn.execute(text(query))
                conn.commit()
                if description:
                    logging.info(f"✅ {description}")
            except Exception as e:
                logging.error(f"❌ Error: {str(e)}")
                raise

    def define_tables(self, models_folder: Path) -> None:
        """Define database table structures from SQL files"""
        if not self.engine:
            raise ValueError("Database not connected")
    
        for sql_file in sorted(models_folder.glob("*.sql")):
            with open(sql_file, 'r') as f:
                self._execute_query(f.read(), f"Defined table from {sql_file.name}")
    
    def set_constraints(self, constraints_folder: Path) -> None:
        """Set constraints on existing tables"""
        if not self.engine:
            raise ValueError("Database not connected")
    
        for sql_file in sorted(constraints_folder.glob("*.sql")):
            with open(sql_file, 'r') as f:
                self._execute_query(f.read(), f"Set constraints from {sql_file.name}")
    
    def initialize_data(self, seeds_folder: Path) -> None:
        """Initialize tables with reference data"""
        if not self.engine:
            raise ValueError("Database not connected")
    
        for sql_file in sorted(seeds_folder.glob("*.sql")):
            with open(sql_file, 'r') as f:
                self._execute_query(f.read(), f"Initialized data from {sql_file.name}")


# Constants with type hints
LOCAL_DB_FOLDER: Final[Path] = Path('data')
LOCAL_DB_NAME: Final[str] = 'windmanager_test.db'
LOCAL_DB_PATH: Final[Path] = LOCAL_DB_FOLDER / LOCAL_DB_NAME


class LocalDatabase(Database):
    @classmethod
    def connect(cls):
        """Returns a context manager for the local test database"""
        return cls().switch_on(Engine(local_connection=LOCAL_DB_PATH))
    
