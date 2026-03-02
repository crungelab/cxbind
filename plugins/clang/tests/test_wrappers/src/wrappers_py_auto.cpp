#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include "wrappers.h"

namespace py = pybind11;

void register_wrappers_py_auto(py::module &_tests, Registry &registry) {
    _tests
    .def("test_wrapper", [](const SDLWindowWrapper& window)
        {
            testWrapper(window.get());
            return ;
        }
        , py::arg("window")
        , py::return_value_policy::automatic_reference)
    ;


}