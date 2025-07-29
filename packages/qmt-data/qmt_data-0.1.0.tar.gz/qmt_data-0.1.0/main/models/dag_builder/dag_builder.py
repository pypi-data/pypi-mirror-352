import json
import os
import yaml
from jinja2 import Environment, FileSystemLoader

from main.models.project.project import Project

TEMPLATE_DIR = 'resources/templates'


class DagBuilder:
    def __init__(self, project: Project, table_name, incremental_column):
        self.project = project
        self.table_name = table_name
        self.incremental_column = incremental_column
        self.env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            trim_blocks=True,
            lstrip_blocks=True
        )

    @staticmethod
    def load_yaml_config(file_path):
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)

    def render_template(self, template_name, context):
        template = self.env.get_template(template_name)
        return template.render(context)

    def generate_dag_file(self, dag_id, schedule_interval):
        config = {
            'dag_id': dag_id,
            'schedule_interval': schedule_interval,
            'connections': self.project.get_connections(),
            'table_name': self.table_name,
            'incremental_column': self.incremental_column
        }
        dag_id = config['dag_id']
        source = config['connections']['source']['type'].lower()
        temp = config['connections']['temp_storage']['type'].lower()
        target = config['connections']['target']['type'].lower()
        # Template selections (use defaults if not set)
        export_template = f'EXPORT/export_{source}_to_{temp}.py.j2'
        load_template = f'LOAD/load_{temp}_to_{target}.py.j2'
        get_last_loaded_value = f'LAST_LOADED/get_last_loaded_value_{target}.py.j2'
        delete_temp_file = f'TEMP/delete_from_{temp}.py.j2'
        truncate_target_table = f'TRUNCATE/truncate_{target}.py.j2'
        dag_wrapper_template = 'dag_template_incremental.py.j2' if self.incremental_column else 'dag_template_full.py.j2'


        # Render task blocks
        context = {'config': config}
        export_task_code = self.render_template(export_template, context)
        load_task_code = self.render_template(load_template, context)
        get_last_loaded_value_code = self.render_template(get_last_loaded_value, context)
        delete_temp_file_code = self.render_template(delete_temp_file, context)
        truncate_target_table_code = self.render_template(truncate_target_table, context)

        # Render final DAG
        full_dag_code = self.render_template(dag_wrapper_template, {
            'dag_id': dag_id,
            'schedule_interval': config['schedule_interval'],
            'export_task': export_task_code,
            'load_task': load_task_code,
            'get_last_loaded_value': get_last_loaded_value_code,
            'delete_temp_file': delete_temp_file_code,
            'truncate_target_table': truncate_target_table_code
        })

        output_file_path = os.path.join(self.project.directory, "dags", f'{dag_id}.py')
        with open(output_file_path, 'w') as f:
            f.write(full_dag_code)

        print(f"Generated DAG file: {output_file_path}")

    # def main():
    #     os.makedirs(OUTPUT_DIR, exist_ok=True)
    #     for filename in os.listdir(CONFIG_DIR):
    #         if filename.endswith('.yaml') or filename.endswith('.yml'):
    #             full_path = os.path.join(CONFIG_DIR, filename)
    #             generate_dag_file(full_path)

#
# if __name__ == '__main__':
#     db = DagBuilder(Project.from_json('local_airflow'), 'users')
#     db.generate_dag_file('test_templated_dag', '@daily')
