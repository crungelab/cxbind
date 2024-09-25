#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "enums.h"

namespace py = pybind11;

void init_generated(py::module &_core, Registry &registry) {
    py::enum_<SimpleEnum>(_core, "SimpleEnum", py::arithmetic())
        .value("ENUM_VALUE_1", SimpleEnum::ENUM_VALUE_1)
        .value("ENUM_VALUE_2", SimpleEnum::ENUM_VALUE_2)
        .value("ENUM_VALUE_3", SimpleEnum::ENUM_VALUE_3)
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

    py::enum_<ns::RedundantEnum>(_core, "RedundantEnum", py::arithmetic())
        .value("VALUE1", ns::RedundantEnum::RedundantEnumValue1)
        .value("VALUE2", ns::RedundantEnum::RedundantEnumValue2)
        .value("VALUE3", ns::RedundantEnum::RedundantEnumValue3)
        .export_values()
    ;


}