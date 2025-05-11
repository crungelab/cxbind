
from pathlib import Path
import yaml
from loguru import logger

from cxbind.unit import Unit
from cxbind.project import Project


# Load the YAML file
file_path = Path('test_project.yaml')
with open(file_path, 'r') as file:
    yaml_data = yaml.safe_load(file)

logger.debug(f"yaml_data: {yaml_data}")

# Process the entries
data = {}
for key, value in yaml_data.items():
    if '/' in key:
        kind, name = key.split('/')
        value['name'] = name
        value['kind'] = kind
        if kind in data:
            data[kind].append(value)
        else:
            data[kind] = [value]
    else:
        data[key] = value

logger.debug(f"processed_data: {data}")

# Validate with Pydantic
project = Project.model_validate(data)

logger.debug(f"project: {project}")

# Dump the Pydantic model
logger.debug(f"project.json(): {project.model_dump_json()}")
