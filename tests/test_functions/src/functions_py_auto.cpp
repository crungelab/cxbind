#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "functions.h"

namespace py = pybind11;

void register_functions_py_auto(py::module &_core, Registry &registry) {
    _core
    .def("add", &test_functions::add
        , py::arg("x")
        , py::arg("y")
        , py::return_value_policy::automatic_reference)

    .def("sub", &test_functions::sub
        , py::arg("x")
        , py::arg("y")
        , py::return_value_policy::automatic_reference)
    ;


}