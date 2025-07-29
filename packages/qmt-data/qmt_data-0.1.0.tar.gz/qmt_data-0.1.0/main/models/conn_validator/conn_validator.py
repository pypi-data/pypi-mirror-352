import json
import logging

from sqlalchemy import create_engine, Engine, text
from sqlalchemy.exc import SQLAlchemyError

from main.models.project.project import Project

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

SOURCES_TYPES = ['mysql', 'postgres']
TEMP_TYPES = ['gcs']
TARGET_TYPES = ['bigquery']


class ConnectionValidator:
    def __init__(self, project: Project):
        self.project = project
        self.connections_dir = f'{self.project.directory}/QMT/connections.json'

    def validate(self) -> bool:
        with open(self.connections_dir, 'r', encoding='utf-8') as f:
            connections: dict = json.load(f)

        with open('resources/prototypes/connections.json', 'r', encoding='utf-8') as f:
            connections_proto: dict = json.load(f)

        # keys check

        if set(connections) != set(connections_proto) or set(connections['source']) != set(
                connections_proto['source']) or set(connections['temp_storage']) != set(
            connections_proto['temp_storage']) or set(connections['target']) != set(connections_proto['target']):
            logger.error('Connections key-set do not match to initially provided')
            return False
        logger.info('Connections key-set is valid')
        # types check
        if connections['source']['type'] not in SOURCES_TYPES or connections['temp_storage']['type'] not in TEMP_TYPES or connections['target']['type'] not in TARGET_TYPES:
            logger.error('Not all of the systems provided are supported')
            return False
        logger.info('All systems are supported')
        # source connection check
        engine: Engine
        if connections['source']['type'] == 'mysql':
            source = connections['source']
            engine = create_engine(
                f"mysql+pymysql://{source['user']}:{source['password']}@{source['host']}:{source['port']}/{source['database']}")
        elif connections['source']['type'] == 'postgres':
            source = connections['source']
            engine = create_engine(
                f"postgresql+psycopg2://{source['user']}:{source['password']}@{source['host']}:{source['port']}/{source['database']}"
            )
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except SQLAlchemyError as e:
            logger.error('Source connection error: {}'.format(e))
            return False
        logger.info('Source connection is valid')
        return True





if __name__ == '__main__':
    c = ConnectionValidator(Project.get_current_project())
    c.validate()
