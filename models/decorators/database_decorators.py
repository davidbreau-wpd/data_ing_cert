import functools
from pathlib import Path
from ..DataBase import Database, Engine

# Chemins SQL définis une seule fois
SQL_MODELS_PATH = Path('sql/models')
SQL_CONSTRAINTS_PATH = Path('sql/constraints')
SQL_SEEDS_PATH = Path('sql/seeds')

def with_local_db(db_name="windmanager_test.db", db_folder="data"):
    """
    Decorator that provides a database connection to the decorated function.
    
    Args:
        db_name: Name of the database file
        db_folder: Folder containing the database
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            db_path = Path(db_folder) / db_name
            with Database().switch_on(Engine(local_connection=db_path)) as db:
                return func(db, *args, **kwargs)
        return wrapper
    return decorator

# Fonctions prédéfinies avec décorateur
@with_local_db()
def build_database(db):
    """Crée la base de données"""
    db.build()

@with_local_db()
def setup_full_database(db):
    """Configure la base de données complète"""
    db.define_tables(SQL_MODELS_PATH)
    db.set_constraints(SQL_CONSTRAINTS_PATH)
    db.initialize_data(SQL_SEEDS_PATH)