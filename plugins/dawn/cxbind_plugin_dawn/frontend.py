from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .program import Program

from pathlib import Path
import json
from pydantic import ValidationError
from loguru import logger

from .processor import Processor
from .node import Root, ObjectType, EnumType, BitmaskType, StructureType

def filter_dawn_data(data: dict) -> dict:
    """Filter out special keys and items without a 'category' field."""
    return {
        k: v
        for k, v in data.items()
        if isinstance(v, dict)
        and "category" in v
        and k not in ["_comment", "_doc", "_metadata"]
    }


class Frontend(Processor):
    def __init__(self, program: "Program") -> None:
        super().__init__(program)

    def run(self):
        #path = Path("../../depot/dawn/src/dawn/dawn.json")
        #path = Path("../../depot/skia/third_party/externals/dawn/src/dawn/dawn.json")
        path = Path(self.program.unit.source)
        try:
            with open(path, "r") as f:
                dawn_data = json.load(f)

            # Filter the data before parsing
            filtered_data = filter_dawn_data(dawn_data)
            #print(filtered_data["buffer"])
            '''
            for k, v in filtered_data.items():
                print(k)
            exit()
            '''
            root = Root.model_validate(filtered_data)
            #print(root["buffer"])
            #exit()
            self.program.root = root

        except json.JSONDecodeError:
            print("Error decoding JSON")
            exit()
        except ValidationError as e:
            print(f"Validation error: {e}")
            exit()
