
import yaml
from pathlib import Path
from loguru import logger
from cxbind.unit import Unit

# Load the YAML file
file_path = Path('test_config.yaml')
with open(file_path, 'r') as file:
    yaml_data = yaml.safe_load(file)

logger.debug(f"yaml_data: {yaml_data}")

# Validate with Pydantic
#unit = Unit(**yaml_data)
unit = Unit.model_validate(yaml_data)

logger.debug(f"unit: {unit}")

# Dump the Pydantic model
logger.debug(f"unit.json(): {unit.model_dump_json()}")
