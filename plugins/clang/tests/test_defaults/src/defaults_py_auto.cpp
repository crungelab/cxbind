#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "defaults.h"

namespace py = pybind11;

void register_defaults_py_auto(py::module &_tests, Registry &registry) {
    py::enum_<DefaultsEnum>(_tests, "DefaultsEnum", py::arithmetic())
        .value("DEFAULTS_ENUM_1", DefaultsEnum::DEFAULTS_ENUM_1)
        .value("DEFAULTS_ENUM_2", DefaultsEnum::DEFAULTS_ENUM_2)
        .value("DEFAULTS_ENUM_3", DefaultsEnum::DEFAULTS_ENUM_3)
        .value("DEFAULTS_ENUM_4", DefaultsEnum::DEFAULTS_ENUM_4)
        .value("DEFAULTS_ENUM_5", DefaultsEnum::DEFAULTS_ENUM_5)
        .value("DEFAULTS_ENUM_6", DefaultsEnum::DEFAULTS_ENUM_6)
        .value("DEFAULTS_ENUM_7", DefaultsEnum::DEFAULTS_ENUM_7)
        .value("DEFAULTS_ENUM_8", DefaultsEnum::DEFAULTS_ENUM_8)
        .value("DEFAULTS_ENUM_9", DefaultsEnum::DEFAULTS_ENUM_9)
        .value("DEFAULTS_ENUM_10", DefaultsEnum::DEFAULTS_ENUM_10)
        .export_values()
    ;
    py::enum_<DefaultsEnumClass>(_tests, "DefaultsEnumClass", py::arithmetic())
        .value("DEFAULTS_ENUM_CLASS_1", DefaultsEnumClass::DEFAULTS_ENUM_CLASS_1)
        .value("DEFAULTS_ENUM_CLASS_2", DefaultsEnumClass::DEFAULTS_ENUM_CLASS_2)
        .value("DEFAULTS_ENUM_CLASS_3", DefaultsEnumClass::DEFAULTS_ENUM_CLASS_3)
        .value("DEFAULTS_ENUM_CLASS_4", DefaultsEnumClass::DEFAULTS_ENUM_CLASS_4)
        .value("DEFAULTS_ENUM_CLASS_5", DefaultsEnumClass::DEFAULTS_ENUM_CLASS_5)
        .value("DEFAULTS_ENUM_CLASS_6", DefaultsEnumClass::DEFAULTS_ENUM_CLASS_6)
        .value("DEFAULTS_ENUM_CLASS_7", DefaultsEnumClass::DEFAULTS_ENUM_CLASS_7)
        .value("DEFAULTS_ENUM_CLASS_8", DefaultsEnumClass::DEFAULTS_ENUM_CLASS_8)
        .value("DEFAULTS_ENUM_CLASS_9", DefaultsEnumClass::DEFAULTS_ENUM_CLASS_9)
        .value("DEFAULTS_ENUM_CLASS_10", DefaultsEnumClass::DEFAULTS_ENUM_CLASS_10)
        .export_values()
    ;
    py::class_<Defaults> _Defaults(_tests, "Defaults");
    registry.on(_tests, "Defaults", _Defaults);
        py::enum_<Defaults::InnerEnum>(_Defaults, "InnerEnum", py::arithmetic())
            .value("INNER_ENUM_1", Defaults::InnerEnum::INNER_ENUM_1)
            .value("INNER_ENUM_2", Defaults::InnerEnum::INNER_ENUM_2)
            .value("INNER_ENUM_3", Defaults::InnerEnum::INNER_ENUM_3)
            .value("INNER_ENUM_4", Defaults::InnerEnum::INNER_ENUM_4)
            .value("INNER_ENUM_5", Defaults::InnerEnum::INNER_ENUM_5)
            .value("INNER_ENUM_6", Defaults::InnerEnum::INNER_ENUM_6)
            .value("INNER_ENUM_7", Defaults::InnerEnum::INNER_ENUM_7)
            .value("INNER_ENUM_8", Defaults::InnerEnum::INNER_ENUM_8)
            .value("INNER_ENUM_9", Defaults::InnerEnum::INNER_ENUM_9)
            .value("INNER_ENUM_10", Defaults::InnerEnum::INNER_ENUM_10)
            .export_values()
        ;
        _Defaults
        .def(py::init<>())
        .def("add", &Defaults::add
            , py::arg("i") = 0
            , py::arg("j") = DefaultsEnum::DEFAULTS_ENUM_1
            , py::return_value_policy::automatic_reference)
        .def("subtract", &Defaults::subtract
            , py::arg("i") = 0
            , py::arg("j") = Defaults::InnerEnum::INNER_ENUM_1
            , py::return_value_policy::automatic_reference)
        .def("multiply", &Defaults::multiply
            , py::arg("i")
            , py::arg("j")
            , py::return_value_policy::automatic_reference)
    ;


}