import yaml
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Date, DateTime
from pathlib import Path

class Database:
    def __init__(self, db_file="data/wpd_windmanager_test_database.db"):
        db_path = Path(db_file)
        self.db_url = f"sqlite:///{db_path}"
        self.engine = create_engine(self.db_url)
        self.metadata = MetaData()
        
    def _load_dbt_models(self):
        dbt_path = Path("dbt") / "models"
        for yml_file in dbt_path.glob("**/*.yml"):
            with open(yml_file) as f:
                model_def = yaml.safe_load(f)
                if model_def.get("version") == 2:
                    for model in model_def.get("models", []):
                        self._create_table_from_model(model)
    
    def _create_table_from_model(self, model):
        columns = []
        for col in model.get("columns", []):
            col_type = self._get_sqlalchemy_type(col["type"])
            columns.append(Column(col["name"], col_type))
        
        Table(model["name"], self.metadata, *columns)
    
    def build(self):
        """Creates database and tables from dbt models"""
        self._load_dbt_models()
        self.metadata.create_all(self.engine)