import json
import os

from main.models.dag_builder.dag_builder import DagBuilder
from main.models.project.project import Project
import logging

from main.models.schema_creator.schema_creator import SchemaCreator
from main.models.schema_validator.schema_validator import SchemaValidator

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class Controller:
    @staticmethod
    def add_project_to_json_file(file_path, name, dir_value):
        new_object = {
            "name": name,
            "dir": dir_value
        }

        data = []

        # If the file exists and is not empty, try to load the content
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, 'r') as file:
                try:
                    data = json.load(file)
                    if not isinstance(data, list):
                        raise ValueError("JSON file does not contain an array.")
                except json.JSONDecodeError:
                    raise ValueError("Invalid JSON in file.")

        # Append the new object
        data.append(new_object)

        # Write back the updated list
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)

    @staticmethod
    def create_project(args):
        logger.info(f'Creating QMT project "{args.name}", dir - "{args.dir}"')

        pr = Project(args.name, args.dir, args.desc)
        pr.save()

    @staticmethod
    def open_project(args):
        pr = Project.from_json(args.name)
        pr.make_current()
        logger.info(f'Opened QMT project "{pr}"')

    @staticmethod
    def list_projects(args):
        Project.list_all_projects()

    @staticmethod
    def generate_dags(args):
        project = Project.get_current_project()
        logger.info('Validating migration schema')
        if SchemaValidator(project).validate():
            logger.info('Generating DAGs...')
            migration_schema = project.get_migration_schema()
            for table in migration_schema['tables']:
                dag_generator = DagBuilder(project, table['name'], table.get('incremental_load_column'))
                dag_generator.generate_dag_file(migration_schema['prefix'] + table['name'], migration_schema['schedule_interval'])
        else:
            logger.error("Schema validation error")
            return False

    @staticmethod
    def generate_schema(args):
        project = Project.get_current_project()
        schema_creator = SchemaCreator(project)
        schema_creator.create_schema()

