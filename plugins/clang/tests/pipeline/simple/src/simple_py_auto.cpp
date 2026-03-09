#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "simple.h"

namespace py = pybind11;

void register_simple_py_auto(py::module &_tests, Registry &registry) {
    py::class_<Simple> _Simple(_tests, "Simple");
    registry.on(_tests, "Simple", _Simple);
        _Simple
        .def(py::init<>())
        .def("add", &Simple::add
            , py::arg("i")
            , py::arg("j")
            , py::return_value_policy::automatic_reference)
        .def("sub", &Simple::sub
            , py::arg("i")
            , py::arg("j")
            , py::return_value_policy::automatic_reference)
    ;


}