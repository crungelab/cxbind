#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "aliases.h"

namespace py = pybind11;

void register_aliases_py_auto(py::module &_tests, Registry &registry) {
    _tests
    .def("facade_function", &facadeFunction
        , py::arg("a")
        , py::arg("b")
        , py::return_value_policy::automatic_reference)
    ;


}