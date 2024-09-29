from typing import List, Optional
from pathlib import Path

from loguru import logger
import yaml


class UnitBaseLoader:
    def load_yaml(self, path: Path) -> dict:
        # Load the YAML file
        with open(path, 'r') as file:
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
        return data