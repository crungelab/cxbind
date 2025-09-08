#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "enums.h"

namespace py = pybind11;

void register_enums_py_auto(py::module &_core, Registry &registry) {
    py::enum_<SimpleEnum>(_core, "SimpleEnum", py::arithmetic())
        .value("VALUE_1", SimpleEnum::VALUE_1)
        .value("VALUE_2", SimpleEnum::VALUE_2)
        .value("VALUE_3", SimpleEnum::VALUE_3)
        .export_values()
    ;
    py::enum_<ScopedEnum>(_core, "ScopedEnum", py::arithmetic())
        .value("VALUE1", ScopedEnum::Value1)
        .value("VALUE2", ScopedEnum::Value2)
        .value("VALUE3", ScopedEnum::Value3)
        .export_values()
    ;
    py::enum_<RedundantEnum>(_core, "RedundantEnum", py::arithmetic())
        .value("VALUE1", RedundantEnum::RedundantEnumValue1)
        .value("VALUE2", RedundantEnum::RedundantEnumValue2)
        .value("VALUE3", RedundantEnum::RedundantEnumValue3)
        .export_values()
    ;
    py::enum_<ns::NsRedundantEnum>(_core, "NsRedundantEnum", py::arithmetic())
        .value("VALUE1", ns::NsRedundantEnum::NsRedundantEnumValue1)
        .value("VALUE2", ns::NsRedundantEnum::NsRedundantEnumValue2)
        .value("VALUE3", ns::NsRedundantEnum::NsRedundantEnumValue3)
        .export_values()
    ;
    py::enum_<TypedefEnum>(_core, "TypedefEnum", py::arithmetic())
        .value("VALUE1", TypedefEnum::TypedefEnumValue1)
        .value("VALUE2", TypedefEnum::TypedefEnumValue2)
        .value("VALUE3", TypedefEnum::TypedefEnumValue3)
        .export_values()
    ;
    py::class_<EnumStruct> EnumStruct(_core, "EnumStruct");
    registry.on(_core, "EnumStruct", EnumStruct);

}