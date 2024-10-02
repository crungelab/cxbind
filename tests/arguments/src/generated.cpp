#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "arguments.h"

namespace py = pybind11;

void init_generated(py::module &_core, Registry &registry) {
    PYCLASS(_core, Test, Test)
        .def(py::init<>())

        .def("add", &Test::add
            , py::arg("i") = 0
            , py::arg("j") = 0
            , py::return_value_policy::automatic_reference)
    ;


}