#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "simple.h"

namespace py = pybind11;

void register_simple_py_auto(py::module &_core, Registry &registry) {
    PYCLASS(_core, Simple, Simple)

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