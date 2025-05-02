import yaml; import logging
from pathlib import Path 
from contextlib import contextmanager
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime

from enums import DatabaseType as Type


class Engine:
    def __init__(self, local_connection: Path = None, azure_connection: dict = None):
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
        self.metadata = MetaData()
        self._type_mapping = {
            'integer': Integer,
            'string': String,
            'float': Float,
            'datetime': DateTime
        }

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
    
    def build(self):
        """Just creates the database if it doesn't exist"""
        if not self.engine:
            raise ValueError("Database not connected")
        with self.engine.connect() as conn:
            pass
    
    def set_tables(self, yaml_folder: Path):
        """Set database tables based on YAML configuration files"""
        if not self.engine:
            raise ValueError("Database not connected")

        for yaml_file in yaml_folder.glob("*.yaml"):
            with open(yaml_file, 'r') as f:
                table_config = yaml.safe_load(f)
                
            table_name = table_config['table_name']
            columns = []
            
            for col in table_config['columns']:
                col_type = self._type_mapping.get(col['type'].lower())
                if not col_type:
                    raise ValueError(f"Unknown column type: {col['type']}")
                
                columns.append(Column(
                    col['name'],
                    col_type,
                    primary_key=col.get('primary_key', False),
                    nullable=col.get('nullable', True)
                ))
            
            Table(table_name, self.metadata, *columns)
        
        self.metadata.create_all(self.engine)

    def drop_tables(self):
        """Drops all tables"""
        confirm = input("\n⚠️ Are you sure you want to drop all tables? (y/N): ")
        if confirm.lower() != 'y':
            raise Exception("❌ Operation cancelled by user")
            
        self.metadata.drop_all(self.engine)
        logging.info("✅ All tables dropped")
    
    def delete(self):
        """Delete the database and close all connections"""
        confirm = input("\n⚠️ Are you sure you want to delete the database? (y/N): ")
        if confirm.lower() != 'y':
            raise Exception("❌ Operation cancelled by user")
            
        # Drop all tables first
        self.drop_tables()
        
        # Close connection and dispose engine
        if self.engine:
            self.engine.dispose()
            
        logging.info("✅ Database deleted")
    
