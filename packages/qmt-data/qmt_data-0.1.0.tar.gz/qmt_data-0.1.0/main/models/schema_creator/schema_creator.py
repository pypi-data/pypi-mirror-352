import json

from sqlalchemy import create_engine, inspect, Engine, Date, DateTime
import logging

from main.models.conn_validator.conn_validator import ConnectionValidator
from main.models.project.project import Project

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)
# Replace with your actual MySQL credentials
username = 'your_user'
password = 'your_password'
host = 'localhost'
port = 3306
database = 'your_database'


class SchemaCreator:
    def __init__(self, project: Project):
        self.project = project
        self.migration_schema_dir = f'{self.project.directory}/QMT/migration_schema.json'
        self.connections_dir = f'{self.project.directory}/QMT/connections.json'

    def create_schema(self):
        logger.info('Validating connections config')
        if ConnectionValidator(self.project).validate():
            with open(self.connections_dir, 'r', encoding='utf-8') as f:
                connections = json.load(f)
            source = connections['source']
            source_type = connections['source']['type'].lower()
            engine: Engine
            if source_type == 'mysql':
                engine = create_engine(
                    f"mysql+pymysql://{source['user']}:{source['password']}@{source['host']}:{source['port']}/{source['database']}")
            else:
                logger.warning(f'Unsupported source type: {source_type}')
                return
            inspector = inspect(engine)

            # Get all table names
            tables = inspector.get_table_names()
            migration_schema_dict = {"schedule_interval": "@daily", "prefix": "QMT_GENERATED_DAG_",
                                     "tables": []}
            for table in tables:
                columns = inspector.get_columns(table)
                date_columns = [
                    col['name'] for col in columns
                    if isinstance(col['type'], (Date, DateTime))
                ]
                if len(date_columns) > 0:
                    migration_schema_dict['tables'].append({'name': table, 'incremental_load_column': date_columns[0]})
                else:
                    migration_schema_dict['tables'].append({'name': table})

            with open(self.migration_schema_dir, 'w') as f:
                json.dump(migration_schema_dict, f, indent=2)
            logger.info(f'Migration schema created at {self.migration_schema_dir}')
        else:
            logger.error('Connection file is corrupted')
