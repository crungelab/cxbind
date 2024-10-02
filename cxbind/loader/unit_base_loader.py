from typing import List, Optional
from pathlib import Path

from loguru import logger
import yaml


class UnitBaseLoader:
    def load_yaml(self, path: Path) -> dict:
        # Load the YAML file
        with open(path, 'r') as file:
            yaml_data = yaml.safe_load(file)

        #logger.debug(f"yaml_data: {yaml_data}")

        return yaml_data
