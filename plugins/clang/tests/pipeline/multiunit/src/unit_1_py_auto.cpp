#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "unit_1.h"

namespace py = pybind11;

void register_unit_1_py_auto(py::module &_tests, Registry &registry) {
    py::class_<Unit1> _Unit1(_tests, "Unit1");
    registry.on(_tests, "Unit1", _Unit1);
        _Unit1
        .def(py::init<>())
        .def("add", &Unit1::add
            , py::arg("i")
            , py::arg("j")
            , py::return_value_policy::automatic_reference)
        .def("sub", &Unit1::sub
            , py::arg("i")
            , py::arg("j")
            , py::return_value_policy::automatic_reference)
    ;


}