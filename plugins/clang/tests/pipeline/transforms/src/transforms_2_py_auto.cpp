#include <limits>
#include <sstream>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "handles.h"

namespace py = pybind11;

void register_handles_py_auto(py::module &_tests, Registry &registry) {
    _tests
    .def("transforms_create_dummy", &transformsCreateDummy
        , py::arg("handle")
        , py::arg("value")
        , py::return_value_policy::automatic_reference)
    ;


}