
from pathlib import Path
import yaml
from loguru import logger

from cxbind.unit import Unit
from cxbind.factory.project_factory import ProjectFactory


file_path = Path('test_project.yaml')

project = ProjectFactory().load(file_path)

logger.debug(f"project: {project}")

# Dump the Pydantic model
logger.debug(f"project.json(): {project.model_dump_json()}")
