import json

from main.models.project.project import Project
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class SchemaValidator:
    def __init__(self, project: Project):
        self.project = project
        self.migration_schema_dir = f'{self.project.directory}/QMT/migration_schema.json'

    def validate(self) -> bool:
        with open(self.migration_schema_dir, 'r', encoding='utf-8') as f:
            schema: dict = json.load(f)

        with open('resources/prototypes/migration_schema.json', 'r', encoding='utf-8') as f:
            schema_proto: dict = json.load(f)

        if set(schema) != set(schema_proto):
            logger.error('Migration Schema key-set do not match to initially provided')
            return False
        tables: list[dict] = schema['tables']
        for table in tables:
            keys = list(table.keys())
            if 'name' not in keys:
                logger.error('There is table without "name" key')
                logger.error(table)
                return False
            if len(keys) == 1:
                continue
            if 'incremental_load_column' not in keys or len(keys) > 2:
                logger.error('There is table with not relevant configuration keys')
                logger.error(table)
                return False
        logger.info('Migration schema validated')
        return True
