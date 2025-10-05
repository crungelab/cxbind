#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "advanced.h"

namespace py = pybind11;

void register_advanced_py_auto(py::module &_tests, Registry &registry) {
    py::class_<AdvancedStruct> _AdvancedStruct(_tests, "AdvancedStruct");
    registry.on(_tests, "AdvancedStruct", _AdvancedStruct);
        _AdvancedStruct
        .def(py::init<int>()
        , py::arg("value") = 0
        )
        .def("add", &AdvancedStruct::add
            , py::arg("i")
            , py::return_value_policy::automatic_reference)
        .def_readwrite("value", &AdvancedStruct::value)
    ;

    py::class_<AdvancedClass> _AdvancedClass(_tests, "AdvancedClass");
    registry.on(_tests, "AdvancedClass", _AdvancedClass);
        _AdvancedClass
        .def(py::init<int>()
        , py::arg("value") = 0
        )
        .def("add", &AdvancedClass::add
            , py::arg("i")
            , py::return_value_policy::automatic_reference)
        .def("ignore_me", &AdvancedClass::ignore_me
            , py::arg("i")
            , py::return_value_policy::automatic_reference)
        .def_readwrite("value", &AdvancedClass::value)
    ;


}