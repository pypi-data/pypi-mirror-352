import json
import logging
import os
import shutil
from dataclasses import dataclass, asdict
import datetime


logger = logging.getLogger('main')
logger.setLevel(logging.INFO)
PROJECTS_JSON_PATH = 'resources/projects.json'
CURRENT_PROJECTS_JSON_PATH = 'resources/current_project.json'


@dataclass
class Project:
    name: str
    directory: str
    description: str
    created_at: datetime.datetime = datetime.datetime.now(datetime.UTC).isoformat()

    def __post_init__(self):
        if self.name is None or self.directory is None:
            raise ValueError("Project should have a name and a directory")
        if not os.path.exists(self.directory):
            raise ValueError("Directory does not exist")

    def save(self):
        # save metadata
        with open(PROJECTS_JSON_PATH, 'r') as file:
            try:
                data = json.load(file)
                if not isinstance(data, list):
                    raise ValueError("JSON file does not contain an array.")
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON in file.")

        for project in data:
            if project['name'] == self.name:
                raise ValueError(f"Project with name {self.name} already exists")

        data.append(asdict(self))

        with open(PROJECTS_JSON_PATH, 'w') as file:
            json.dump(data, file, indent=2)

        # create folders
        qmt_dir = self.directory + '/QMT'
        conn_filepath = qmt_dir + '/connections.json'
        schema_filepath = qmt_dir + '/migration_schema.json'
        try:
            os.makedirs(qmt_dir, exist_ok=True)
            logger.info(f"QMT directory created successfully.")
            shutil.copy("resources/prototypes/connections.json", conn_filepath)
            shutil.copy("resources/prototypes/migration_schema.json", schema_filepath)
        except PermissionError:
            logger.error(f"Permission denied: Unable to create '{qmt_dir}'.")
            raise PermissionError("Permission denied")

        self.make_current()
        logger.info(f"Project {self.name} saved and opened")

    @staticmethod
    def from_json(name: str):
        with open(PROJECTS_JSON_PATH, 'r') as file:
            data = json.load(file)
            pr: Project
            for project in data:
                if project['name'] == name:
                    pr = Project(project['name'], project['directory'], project['description'])
                    return pr
            raise ValueError(f"Project with name {name} does not exist")

    @staticmethod
    def get_current_project():
        with open(CURRENT_PROJECTS_JSON_PATH, 'r') as file:
            data = json.load(file)
            pr = Project(data['name'], data['directory'], data['description'])
        return pr

    @staticmethod
    def list_all_projects():
        with open(PROJECTS_JSON_PATH, 'r') as file:
            data = json.load(file)
            projects: list[Project] = []
            for project in data:
                projects.append(Project.from_json(project))
        return projects

    def make_current(self):
        with open(CURRENT_PROJECTS_JSON_PATH, 'w') as file:
            json.dump(asdict(self), file, indent=2)

    def get_connections(self) -> dict:
        with open(os.path.join(self.directory, "QMT", "connections.json")) as f:
            connections = json.load(f)
        return connections

    def get_migration_schema(self) -> dict:
        with open(os.path.join(self.directory, "QMT", "migration_schema.json")) as f:
            migration_schema = json.load(f)
        return migration_schema
