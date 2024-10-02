#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "test.h"

namespace py = pybind11;

void init_generated(py::module &_core, Registry &registry) {
    PYCLASS(_core, other::Other, Other)
        .def(py::init<>())

        .def("add", &other::Other::add
            , py::arg("i")
            , py::arg("j")
            , py::return_value_policy::automatic_reference)
    ;

    PYCLASS(_core, test::Test, Test)
        .def(py::init<>())

        .def("add", py::overload_cast<int, int>(&test::Test::add)
            , py::arg("i")
            , py::arg("j")
            , py::return_value_policy::automatic_reference)
    ;


}