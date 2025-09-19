from typing_extensions import Annotated
from typing import List, Dict, Optional, Any, Literal, Union

from pydantic import BaseModel, Field, BeforeValidator, ConfigDict

from loguru import logger


class Spec(BaseModel):
    kind: str
    name: str
    signature: Optional[str] = None
    first_name: Optional[str] = None
    pyname: Optional[str] = None
    exclude: Optional[bool] = False
    overload: Optional[bool] = False
    readonly: Optional[bool] = False

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def key(self) -> str:
        if self.signature:
            return f"{self.kind}/{self.name}/{self.signature}"
        return f"{self.kind}/{self.name}"

    def model_post_init(self, __context: Any) -> None:
        self.first_name = self.name.split("::")[-1]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} kind={self.kind}, name={self.name}, pyname={self.pyname}>"


class TemplateSpec(Spec):
    pass


class Argument(BaseModel):
    default: Optional[Any] = None


class FunctionBaseSpec(Spec):
    arguments: Optional[Dict[str, Argument]] = {}
    return_type: Optional[str] = None
    omit_ret: Optional[bool] = False
    check_result: Optional[bool] = False

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        self.arguments = {
            k: Argument(**v) if isinstance(v, dict) else v
            for k, v in self.arguments.items()
        }


class FunctionSpec(FunctionBaseSpec):
    kind: Literal["function"]


class FunctionTemplateSpecializationSpec(FunctionSpec):
    kind: Literal["function_template_specialization"] = (
        "function_template_specialization"
    )
    args: List[str]


class FunctionTemplateSpec(TemplateSpec):
    kind: Literal["function_template"]
    specializations: List[FunctionTemplateSpecializationSpec] = []


class MethodSpec(FunctionBaseSpec):
    kind: Literal["method"]


class CtorSpec(FunctionBaseSpec):
    kind: Literal["ctor"]


class FieldSpec(Spec):
    kind: Literal["field"]


class Property(BaseModel):
    name: str
    getter: Optional[str] = None
    setter: Optional[str] = None


class StructBaseSpec(Spec):
    extends: Optional[List[str]] = None
    gen_init: bool = False
    gen_kw_init: bool = False
    wrapper: str = None
    holder: Optional[str] = None
    properties: Optional[List[Property]] = []


class StructSpec(StructBaseSpec):
    kind: Literal["struct"]


class ClassSpec(StructBaseSpec):
    kind: Literal["class"]


class ClassTemplateSpecializationSpec(ClassSpec):
    kind: Literal["class_template_specialization"] = "class_template_specialization"
    args: List[str]


class ClassTemplateSpec(TemplateSpec):
    kind: Literal["class_template"]
    specializations: List[ClassTemplateSpecializationSpec] = []


class EnumSpec(Spec):
    kind: Literal["enum"]


SpecUnion = Union[
    StructSpec,
    ClassSpec,
    ClassTemplateSpec,
    FieldSpec,
    FunctionSpec,
    FunctionTemplateSpec,
    MethodSpec,
    CtorSpec,
    EnumSpec,
]


def validate_spec_dict(v: dict[str, Spec]) -> dict[str, Spec]:
    # logger.debug(f"validate_spec_dict: {v}")
    data = {}
    for key, value in v.items():
        if "/" in key:
            kind, name, signature = None, None, None
            parts = key.split("/")
            if len(parts) == 2:
                kind, name = parts
            elif len(parts) == 3:
                kind, name, signature = parts
            value["name"] = name
            value["kind"] = kind
            value["signature"] = signature
            # data[name] = value
            data[key] = value
        else:
            data[key] = value
    return data


SpecDict = Annotated[dict[str, SpecUnion], BeforeValidator(validate_spec_dict)]


def create_spec(key: str, **kwargs: Any) -> SpecUnion:
    kind, name, signature = None, None, None
    parts = key.split("/")
    if len(parts) == 2:
        kind, name = parts
    elif len(parts) == 3:
        kind, name, signature = parts
    else:
        logger.error(f"Invalid spec key: {key}")
        raise ValueError(f"Invalid spec key: {key}")

    spec_cls = {
        "function": FunctionSpec,
        "function_template": FunctionTemplateSpec,
        "method": MethodSpec,
        "ctor": CtorSpec,
        "field": FieldSpec,
        "struct": StructSpec,
        "class": ClassSpec,
        "class_template": ClassTemplateSpec,
        "enum": EnumSpec,
    }.get(kind)

    if spec_cls is None:
        logger.error(f"Unknown spec kind: {kind}")
        raise ValueError(f"Unknown spec kind: {kind}")

    return spec_cls(kind=kind, name=name, signature=signature, **kwargs)
