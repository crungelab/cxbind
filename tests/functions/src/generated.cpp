#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "functions.h"

namespace py = pybind11;

void init_generated(py::module &_core, Registry &registry) {
    _core
    .def("add", &add
        , py::arg("x")
        , py::arg("y")
        , py::return_value_policy::automatic_reference)
    .def("sub", &sub
        , py::arg("x")
        , py::arg("y")
        , py::return_value_policy::automatic_reference)
    ;


}