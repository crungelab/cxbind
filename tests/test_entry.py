
import yaml
from pathlib import Path
from loguru import logger
from cxbind.generator_config import GeneratorConfig

# Load the YAML file
file_path = Path('test_entry.yaml')
with open(file_path, 'r') as file:
    yaml_data = yaml.safe_load(file)

logger.debug(f"yaml_data: {yaml_data}")

# Process the entries
data = {}
for key, value in yaml_data.items():
    if '.' in key:
        kind, name = key.split('.')
        value['fqname'] = name
        value['kind'] = kind
        if kind in data:
            data[kind].append(value)
        else:
            data[kind] = [value]
    else:
        data[key] = value

logger.debug(f"processed_data: {data}")

# Validate with Pydantic
config = GeneratorConfig.model_validate(data)

logger.debug(f"config: {config}")

# Dump the Pydantic model
logger.debug(f"config.json(): {config.model_dump_json()}")
