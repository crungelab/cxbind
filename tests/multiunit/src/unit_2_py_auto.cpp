#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "unit_2.h"

namespace py = pybind11;

void init_unit_2_py_auto(py::module &_multiunit, Registry &registry) {
    PYCLASS(_multiunit, Unit2, Unit2)
        .def(py::init<>())

        .def("add", &Unit2::add
            , py::arg("i")
            , py::arg("j")
            , py::return_value_policy::automatic_reference)
        .def("sub", &Unit2::sub
            , py::arg("i")
            , py::arg("j")
            , py::return_value_policy::automatic_reference)
    ;


}