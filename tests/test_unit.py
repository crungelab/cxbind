
import yaml
from pathlib import Path
from loguru import logger
from cxbind.unit import Unit

# Load the YAML file
file_path = Path('test_unit.yaml')
with open(file_path, 'r') as file:
    yaml_data = yaml.safe_load(file)

logger.debug(f"yaml_data: {yaml_data}")

# Process the entries
data = {}
for key, value in yaml_data.items():
    if '.' in key:
        kind, name = key.split('.')
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
unit = Unit.model_validate(data)

logger.debug(f"unit: {unit}")

# Dump the Pydantic model
logger.debug(f"unit.json(): {unit.model_dump_json()}")
