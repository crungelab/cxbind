
import yaml
from pathlib import Path
from loguru import logger
from cxbind.generator_config import GeneratorConfig

# Load the YAML file
file_path = Path('test_config.yaml')
with open(file_path, 'r') as file:
    yaml_data = yaml.safe_load(file)

logger.debug(f"yaml_data: {yaml_data}")

# Validate with Pydantic
#config = GeneratorConfig(**yaml_data)
config = GeneratorConfig.model_validate(yaml_data)

logger.debug(f"config: {config}")

# Dump the Pydantic model
logger.debug(f"config.json(): {config.model_dump_json()}")
