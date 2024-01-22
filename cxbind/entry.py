from typing import List, Dict, Optional, Any

from pydantic import BaseModel

class Entry(BaseModel):
    """Base class for all entries."""
    kind: str
    fqname: str
    exclude: Optional[bool] = False
    overload: Optional[bool] = False
    readonly: Optional[bool] = False

class Argument(BaseModel):
    default: Optional[Any] = None

class FunctionEntry(Entry):
    #arguments: List[str] = []
    #arguments: Dict[str, Any] = {}
    arguments: Optional[Dict[str, Argument]] = {}
    return_type: Optional[str] = None
    omit_ret: Optional[bool] = False
    check_result: Optional[bool] = False

    def model_post_init(self, __context) -> None:
        self.arguments = {k: Argument(**v) if isinstance(v, dict) else v for k, v in self.arguments.items()}

class CtorEntry(Entry):
    pass

class FieldEntry(Entry):
    pass

class MethodEntry(Entry):
    pass

class StructBaseEntry(Entry):
    constructible: bool = True
    has_constructor: bool = False
    gen_init: bool = False
    gen_kw_init: bool = False
    gen_wrapper: dict = None

class StructEntry(StructBaseEntry):
    pass

class ClassEntry(StructBaseEntry):
    pass

class EnumEntry(Entry):
    pass

class TypedefEntry(Entry):
    pass
