import argparse
import json
import os
import logging

from main.controller.Controller import Controller

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

from main.models.project.project import Project


def main():
    parser = argparse.ArgumentParser(description="Run various commands with specific parameters.")
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    # CREATE PROJECT
    create_project_parser = subparsers.add_parser('create-project', help='Creates new QMT project')
    create_project_parser.add_argument(
        '--name',
        type=str,
        required=True,
        help='Project name'
    )
    create_project_parser.add_argument(
        '--dir',
        type=str,
        required=True,
        help='Main airflow directory of your project'
    )
    # create_project_parser.add_argument(
    #     '--airflow-host',
    #     type=str,
    #     required=True,
    #     help='Airflow instance coordinates, example: http://localhost:8080'
    # )
    # create_project_parser.add_argument(
    #     '--airflow-username',
    #     type=str,
    #     required=True,
    #     help='Username of Airflow instance credentials'
    # )
    # create_project_parser.add_argument(
    #     '--airflow-password',
    #     type=str,
    #     required=True,
    #     help='Password of Airflow instance credentials'
    # )
    create_project_parser.add_argument(
        '--desc',
        type=str,
        required=False,
        help='Project description'
    )

    create_project_parser.set_defaults(func=Controller.create_project)

    # LIST PROJECTS
    list_projects_parser = subparsers.add_parser('list-projects', help='Lists all projects')
    list_projects_parser.set_defaults(func=Controller.list_projects)

    # OPEN PROJECT
    open_project_parser = subparsers.add_parser('open-project', help='Open project')
    open_project_parser.add_argument(
        '--name',
        type=str,
        required=True,
        help='Project name'
    )
    open_project_parser.set_defaults(func=Controller.open_project)

    generate_schema_parser = subparsers.add_parser('generate-schema',
                                                   help='Generates project migration schema based on provided connection to source')

    generate_schema_parser.set_defaults(func=Controller.generate_schema)

    generate_dags_parser = subparsers.add_parser('generate-dags', help='Main command to autogenerate Airflow DAGs')
    generate_dags_parser.set_defaults(func=Controller.generate_dags)
    # Parse and dispatch
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
