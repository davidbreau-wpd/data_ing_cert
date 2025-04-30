from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.sql import text  # Add this import
from pathlib import Path 

import pandas as pd
import os


class DatabaseManager:
    def __init__(self, db_file="data/wpd_windmanager_test_database.db"):
        self.db_url = f"sqlite:///{db_file}"
        self.db_file = db_file
        self.engine = create_engine(self.db_url)
        self.metadata = MetaData()
        self.Session = sessionmaker(bind=self.engine)

    def build(self):
        """Creates database and tables"""
        self.metadata.create_all(self.engine)

    def create_tables_from_sql(self, sql_folder: Path):
        """Creates tables from SQL files in the specified folder"""
        with self.engine.connect() as conn:
            for sql_file in sorted(sql_folder.glob("*.sql")):
                with open(sql_file, 'r') as f:
                    sql = f.read()
                    conn.execute(text(sql))  # Add text() here
                    conn.commit()
                print(f"Executed {os.path.basename(sql_file)}")

    def drop_tables(self):
        """Drops all tables"""
        self.metadata.drop_all(self.engine)

    def delete_file(self):
        """Delete the database file and close all connections"""
        # Close all connections and dispose the engine
        if hasattr(self, 'engine'):
            # Close any active sessions
            if hasattr(self, 'Session'):
                self.Session.close_all()
            # Dispose engine and all its connections
            self.engine.dispose()
        
        # Remove the file if it exists
        if os.path.exists(self.db_file):
            try:
                os.remove(self.db_file)
                print(f"Database file {self.db_file} successfully deleted")
            except PermissionError:
                print(f"Could not delete {self.db_file}. File might be in use.")

    def insert_dataframe(self, table_name: str, dataframe: pd.DataFrame):
        """Insert a DataFrame into a specified table"""
        try:
            dataframe.to_sql(
                name=table_name,
                con=self.engine,
                if_exists='append',
                index=False
            )
            print(f"Successfully inserted {len(dataframe)} rows into {table_name}")
        except Exception as e:
            print(f"Error inserting data into {table_name}: {e}")

    def insert_inspection_checklist(self, dataframe: pd.DataFrame):
        """Insert inspection checklist data into service_reports_checklists table"""
        # Rename columns to match database schema
        df_to_insert = dataframe.rename(columns={
            'no': 'item_number',
            'check_item': 'check_item',
            'result': 'result'
        })
        
        # Select only relevant columns
        df_to_insert = df_to_insert[['item_number', 'check_item', 'result']]
        
        try:
            df_to_insert.to_sql(
                name='service_reports_checklists',
                con=self.engine,
                if_exists='append',
                index=False
            )
            print(f"Successfully inserted {len(df_to_insert)} inspection items")
        except Exception as e:
            print(f"Error inserting inspection checklist: {e}")

    def insert_csv(self, csv_path: str, table_name: str, column_mapping: dict = None):
        """
        Insert CSV file into database with column mapping
        Args:
            csv_path: Path to the CSV file
            table_name: Name of the target table
            column_mapping: Dict mapping CSV columns to DB columns. Example:
                {'csv_col1': 'db_col1', 'csv_col2': 'db_col2'}
        """
        try:
            # Read CSV
            df = pd.read_csv(csv_path)
            
            # Apply column mapping if provided
            if column_mapping:
                df = df.rename(columns=column_mapping)
                # Keep only mapped columns
                df = df[list(column_mapping.values())]
            
            # Insert into database
            df.to_sql(
                name=table_name,
                con=self.engine,
                if_exists='append',
                index=False
            )
            print(f"Successfully inserted {len(df)} rows from {csv_path} into {table_name}")
        except Exception as e:
            print(f"Error inserting data from {csv_path}: {e}")