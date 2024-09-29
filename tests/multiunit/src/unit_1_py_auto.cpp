#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "unit_1.h"

namespace py = pybind11;

void init_unit_1_py_auto(py::module &_multiunit, Registry &registry) {
    PYCLASS(_multiunit, Unit1, Unit1)
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